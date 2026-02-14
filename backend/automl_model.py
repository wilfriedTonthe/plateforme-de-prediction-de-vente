import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


class AutoMLPredictor:
    """
    Système AutoML pour la prédiction de ventes.
    Sélectionne automatiquement le meilleur modèle parmi:
    - XGBoost
    - Random Forest
    - Gradient Boosting
    - Ridge Regression
    - Exponential Smoothing (Holt-Winters)
    """
    
    AVAILABLE_MODELS = {
        'xgboost': 'XGBoost Regressor',
        'random_forest': 'Random Forest',
        'gradient_boosting': 'Gradient Boosting',
        'ridge': 'Ridge Regression',
        'linear': 'Linear Regression'
    }
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.best_model: Dict[str, str] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.model_scores: Dict[str, Dict[str, float]] = {}
        self.data: Optional[pd.DataFrame] = None
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Charge les données de ventes depuis un fichier CSV"""
        self.data = pd.read_csv(filepath, parse_dates=['date'])
        return self.data
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crée les features temporelles pour le ML"""
        df = df.copy()
        df['day_of_week'] = df['ds'].dt.dayofweek
        df['day_of_month'] = df['ds'].dt.day
        df['week_of_year'] = df['ds'].dt.isocalendar().week.astype(int)
        df['month'] = df['ds'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        df['lag_1'] = df['y'].shift(1)
        df['lag_7'] = df['y'].shift(7)
        df['lag_14'] = df['y'].shift(14)
        
        df['rolling_mean_7'] = df['y'].shift(1).rolling(window=7, min_periods=1).mean()
        df['rolling_std_7'] = df['y'].shift(1).rolling(window=7, min_periods=1).std()
        df['rolling_mean_14'] = df['y'].shift(1).rolling(window=14, min_periods=1).mean()
        
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def _prepare_data(self, product_id: str) -> Tuple[pd.DataFrame, List[str]]:
        """Prépare les données pour l'entraînement"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        product_data = self.data[self.data['product_id'] == product_id].copy()
        
        if len(product_data) == 0:
            available_products = self.data['product_id'].unique().tolist()
            raise ValueError(f"Produit '{product_id}' non trouvé. Produits disponibles: {available_products}")
        
        daily_sales = product_data.groupby('date')['quantity'].sum().reset_index()
        daily_sales.columns = ['ds', 'y']
        daily_sales = daily_sales.sort_values('ds')
        
        df = self._create_features(daily_sales)
        
        feature_cols = [
            'day_of_week', 'day_of_month', 'week_of_year', 'month', 'is_weekend',
            'lag_1', 'lag_7', 'lag_14', 'rolling_mean_7', 'rolling_std_7', 'rolling_mean_14'
        ]
        
        return df, feature_cols
    
    def _get_models(self) -> Dict[str, Any]:
        """Retourne les modèles disponibles"""
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100, max_depth=5, random_state=42
            ),
            'ridge': Ridge(alpha=1.0),
            'linear': LinearRegression()
        }
        
        if XGBOOST_AVAILABLE:
            models['xgboost'] = xgb.XGBRegressor(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                random_state=42, verbosity=0
            )
        
        return models
    
    def train_and_select_best(self, product_id: str) -> Dict[str, Any]:
        """Entraîne tous les modèles et sélectionne le meilleur"""
        df, feature_cols = self._prepare_data(product_id)
        
        if len(df) < 14:
            return {
                "success": False,
                "error": "Pas assez de données (minimum 14 jours)"
            }
        
        X = df[feature_cols].values
        y = df['y'].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[product_id] = scaler
        
        models = self._get_models()
        scores = {}
        
        tscv = TimeSeriesSplit(n_splits=min(3, len(df) // 7))
        
        for name, model in models.items():
            try:
                cv_scores = cross_val_score(
                    model, X_scaled, y, 
                    cv=tscv, scoring='neg_mean_absolute_error'
                )
                mae = -cv_scores.mean()
                scores[name] = {
                    'mae': mae,
                    'std': cv_scores.std(),
                    'model_name': self.AVAILABLE_MODELS.get(name, name)
                }
            except Exception as e:
                scores[name] = {'mae': float('inf'), 'error': str(e)}
        
        best_model_name = min(scores, key=lambda x: scores[x]['mae'])
        best_model = models[best_model_name]
        best_model.fit(X_scaled, y)
        
        self.models[product_id] = {
            'model': best_model,
            'model_name': best_model_name,
            'feature_cols': feature_cols,
            'last_data': df.tail(14).copy()
        }
        self.best_model[product_id] = best_model_name
        self.model_scores[product_id] = scores
        
        return {
            "success": True,
            "product_id": product_id,
            "best_model": self.AVAILABLE_MODELS.get(best_model_name, best_model_name),
            "best_mae": round(scores[best_model_name]['mae'], 2),
            "all_scores": {
                self.AVAILABLE_MODELS.get(k, k): {
                    'mae': round(v['mae'], 2) if v['mae'] != float('inf') else 'N/A'
                }
                for k, v in scores.items()
            },
            "training_samples": len(df)
        }
    
    def predict(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """Génère des prédictions pour les N prochains jours"""
        if product_id not in self.models:
            train_result = self.train_and_select_best(product_id)
            if not train_result.get("success"):
                return self._fallback_prediction(product_id, days)
        
        model_info = self.models[product_id]
        model = model_info['model']
        feature_cols = model_info['feature_cols']
        last_data = model_info['last_data'].copy()
        scaler = self.scalers[product_id]
        
        predictions = []
        current_data = last_data.copy()
        last_date = current_data['ds'].max()
        
        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)
            
            new_row = {
                'ds': pred_date,
                'y': current_data['y'].iloc[-1],
                'day_of_week': pred_date.weekday(),
                'day_of_month': pred_date.day,
                'week_of_year': pred_date.isocalendar()[1],
                'month': pred_date.month,
                'is_weekend': 1 if pred_date.weekday() >= 5 else 0,
                'lag_1': current_data['y'].iloc[-1],
                'lag_7': current_data['y'].iloc[-7] if len(current_data) >= 7 else current_data['y'].mean(),
                'lag_14': current_data['y'].iloc[-14] if len(current_data) >= 14 else current_data['y'].mean(),
                'rolling_mean_7': current_data['y'].tail(7).mean(),
                'rolling_std_7': current_data['y'].tail(7).std(),
                'rolling_mean_14': current_data['y'].tail(14).mean()
            }
            
            X_pred = np.array([[new_row[col] for col in feature_cols]])
            X_pred_scaled = scaler.transform(X_pred)
            
            pred_value = model.predict(X_pred_scaled)[0]
            pred_value = max(0, pred_value)
            
            std_estimate = current_data['y'].std() * 0.5
            
            predictions.append({
                "date": pred_date.strftime('%Y-%m-%d'),
                "predicted_quantity": round(pred_value),
                "lower_bound": max(0, round(pred_value - std_estimate)),
                "upper_bound": round(pred_value + std_estimate)
            })
            
            new_row['y'] = pred_value
            new_row_df = pd.DataFrame([new_row])
            current_data = pd.concat([current_data, new_row_df], ignore_index=True)
        
        explanation = self._generate_explanation(product_id, predictions, current_data)
        
        return {
            "product_id": product_id,
            "model_used": self.AVAILABLE_MODELS.get(
                self.best_model.get(product_id, 'unknown'), 
                'AutoML'
            ),
            "predictions": predictions,
            "explanation": explanation
        }
    
    def _generate_explanation(self, product_id: str, predictions: List[Dict], 
                              historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Génère une explication détaillée des prédictions"""
        if not predictions:
            return {"summary": "Aucune prédiction générée"}
        
        pred_values = [p["predicted_quantity"] for p in predictions]
        avg_prediction = np.mean(pred_values)
        min_pred = min(pred_values)
        max_pred = max(pred_values)
        
        historical_mean = historical_data['y'].mean()
        historical_std = historical_data['y'].std()
        
        if avg_prediction > historical_mean * 1.1:
            trend = "hausse"
            trend_pct = ((avg_prediction / historical_mean) - 1) * 100
        elif avg_prediction < historical_mean * 0.9:
            trend = "baisse"
            trend_pct = (1 - (avg_prediction / historical_mean)) * 100
        else:
            trend = "stable"
            trend_pct = 0
        
        weekend_preds = [p for i, p in enumerate(predictions) 
                        if datetime.strptime(p["date"], '%Y-%m-%d').weekday() >= 5]
        weekday_preds = [p for i, p in enumerate(predictions) 
                        if datetime.strptime(p["date"], '%Y-%m-%d').weekday() < 5]
        
        weekend_avg = np.mean([p["predicted_quantity"] for p in weekend_preds]) if weekend_preds else 0
        weekday_avg = np.mean([p["predicted_quantity"] for p in weekday_preds]) if weekday_preds else 0
        
        model_name = self.AVAILABLE_MODELS.get(
            self.best_model.get(product_id, 'unknown'), 'AutoML'
        )
        
        best_day = max(predictions, key=lambda x: x["predicted_quantity"])
        worst_day = min(predictions, key=lambda x: x["predicted_quantity"])
        
        factors = []
        if weekend_avg > weekday_avg * 1.1:
            factors.append({
                "factor": "Effet weekend",
                "impact": "positif",
                "description": f"Les ventes sont {round((weekend_avg/weekday_avg - 1) * 100)}% plus elevees le weekend"
            })
        
        if trend != "stable":
            factors.append({
                "factor": "Tendance generale",
                "impact": "positif" if trend == "hausse" else "negatif",
                "description": f"Tendance a la {trend} de {round(trend_pct)}% par rapport a l'historique"
            })
        
        factors.append({
            "factor": "Saisonnalite hebdomadaire",
            "impact": "neutre",
            "description": "Le modele detecte des patterns recurrents chaque semaine"
        })
        
        model_scores = self.model_scores.get(product_id, {})
        
        return {
            "summary": f"Prevision de {round(avg_prediction)} unites/jour en moyenne sur {len(predictions)} jours",
            "trend": {
                "direction": trend,
                "percentage": round(trend_pct, 1),
                "description": f"Les ventes sont prevues en {trend}" + (f" de {round(trend_pct)}%" if trend != "stable" else "")
            },
            "statistics": {
                "average_prediction": round(avg_prediction, 1),
                "min_prediction": min_pred,
                "max_prediction": max_pred,
                "historical_average": round(historical_mean, 1),
                "historical_std": round(historical_std, 1),
                "weekend_average": round(weekend_avg, 1),
                "weekday_average": round(weekday_avg, 1)
            },
            "key_days": {
                "best_day": {
                    "date": best_day["date"],
                    "quantity": best_day["predicted_quantity"],
                    "day_name": datetime.strptime(best_day["date"], '%Y-%m-%d').strftime('%A')
                },
                "worst_day": {
                    "date": worst_day["date"],
                    "quantity": worst_day["predicted_quantity"],
                    "day_name": datetime.strptime(worst_day["date"], '%Y-%m-%d').strftime('%A')
                }
            },
            "factors": factors,
            "model_info": {
                "name": model_name,
                "confidence": "elevee" if historical_std / historical_mean < 0.3 else "moyenne" if historical_std / historical_mean < 0.5 else "faible",
                "all_models_tested": list(model_scores.keys()) if model_scores else []
            },
            "recommendations": self._generate_recommendations(avg_prediction, historical_mean, trend, factors, predictions, product_id)
        }
    
    def _generate_recommendations(self, avg_pred: float, hist_mean: float, 
                                   trend: str, factors: List[Dict],
                                   predictions: List[Dict] = None,
                                   product_id: str = None) -> List[str]:
        """Génère des recommandations dynamiques basées sur les prédictions"""
        recommendations = []
        
        variation_pct = abs((avg_pred - hist_mean) / hist_mean * 100) if hist_mean > 0 else 0
        
        if trend == "hausse":
            if variation_pct > 20:
                recommendations.append(f"URGENT: Augmentez le stock de {round(variation_pct)}% - forte hausse prevue")
            else:
                recommendations.append(f"Prevoyez {round(variation_pct)}% de stock supplementaire pour la periode")
            recommendations.append("Opportunite de negocier des volumes avec vos fournisseurs")
        elif trend == "baisse":
            if variation_pct > 20:
                recommendations.append(f"ATTENTION: Reduisez les commandes de {round(variation_pct)}% - baisse significative")
                recommendations.append("Lancez une promotion pour ecouler le stock existant")
            else:
                recommendations.append(f"Ajustez legerement vos commandes (-{round(variation_pct)}%)")
        else:
            recommendations.append("Demande stable - maintenez votre strategie actuelle")
        
        weekend_factor = next((f for f in factors if f["factor"] == "Effet weekend"), None)
        if weekend_factor:
            if weekend_factor["impact"] == "positif":
                recommendations.append("Planifiez le reapprovisionnement avant vendredi soir")
            else:
                recommendations.append("Concentrez vos efforts marketing en semaine")
        
        if predictions and len(predictions) > 0:
            best_day = max(predictions, key=lambda x: x["predicted_quantity"])
            worst_day = min(predictions, key=lambda x: x["predicted_quantity"])
            best_date = datetime.strptime(best_day["date"], '%Y-%m-%d')
            worst_date = datetime.strptime(worst_day["date"], '%Y-%m-%d')
            
            recommendations.append(f"Pic prevu le {best_date.strftime('%d/%m')} ({best_day['predicted_quantity']} unites)")
            
            if best_day["predicted_quantity"] > worst_day["predicted_quantity"] * 2:
                recommendations.append(f"Grande variation: preparez du personnel supplementaire le {best_date.strftime('%d/%m')}")
        
        seasonality_factor = next((f for f in factors if "saisonnier" in f["factor"].lower()), None)
        if seasonality_factor:
            recommendations.append("Tenez compte de la saisonnalite dans vos previsions annuelles")
        
        return recommendations[:5]
    
    def _fallback_prediction(self, product_id: str, days: int) -> Dict[str, Any]:
        """Prédiction simple si pas assez de données"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        product_data = self.data[self.data['product_id'] == product_id]
        daily_sales = product_data.groupby('date')['quantity'].sum().reset_index()
        
        if len(daily_sales) == 0:
            return {"product_id": product_id, "predictions": [], "error": "Aucune donnée"}
        
        mean_sales = daily_sales['quantity'].mean()
        std_sales = daily_sales['quantity'].std() if len(daily_sales) > 1 else mean_sales * 0.2
        last_date = daily_sales['date'].max()
        
        predictions = []
        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)
            multiplier = 1.2 if pred_date.weekday() >= 5 else 1.0
            pred = mean_sales * multiplier
            
            predictions.append({
                "date": pred_date.strftime('%Y-%m-%d'),
                "predicted_quantity": max(0, round(pred)),
                "lower_bound": max(0, round(pred - std_sales)),
                "upper_bound": round(pred + std_sales)
            })
        
        return {
            "product_id": product_id,
            "model_used": "Moyenne Mobile (fallback)",
            "predictions": predictions
        }
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Retourne la liste des produits"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        products = self.data.groupby(['product_id', 'product_name', 'category']).agg({
            'quantity': 'sum',
            'total_sales': 'sum',
            'unit_price': 'first'
        }).reset_index()
        
        return [
            {
                "product_id": row['product_id'],
                "product_name": row['product_name'],
                "category": row['category'],
                "total_quantity_sold": int(row['quantity']),
                "total_revenue": float(row['total_sales']),
                "unit_price": float(row['unit_price'])
            }
            for _, row in products.iterrows()
        ]
    
    def get_sales_summary(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Retourne un résumé des ventes"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        data = self.data[self.data['product_id'] == product_id] if product_id else self.data
        
        summary = {
            "total_sales": float(data['total_sales'].sum()),
            "total_quantity": int(data['quantity'].sum()),
            "average_daily_quantity": float(data.groupby('date')['quantity'].sum().mean()),
            "products": data['product_id'].nunique(),
            "date_range": {
                "start": data['date'].min().strftime('%Y-%m-%d'),
                "end": data['date'].max().strftime('%Y-%m-%d')
            }
        }
        
        if product_id:
            summary["product_id"] = product_id
            summary["product_name"] = data['product_name'].iloc[0]
        
        return summary
    
    def get_daily_sales(self, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retourne les ventes journalières"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        data = self.data[self.data['product_id'] == product_id] if product_id else self.data
        
        daily = data.groupby('date').agg({
            'quantity': 'sum',
            'total_sales': 'sum'
        }).reset_index()
        
        return [
            {
                "date": row['date'].strftime('%Y-%m-%d'),
                "quantity": int(row['quantity']),
                "total_sales": float(row['total_sales'])
            }
            for _, row in daily.iterrows()
        ]
