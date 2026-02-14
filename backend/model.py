import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

PROPHET_AVAILABLE = False


class SalesPredictionModel:
    """Modèle de prédiction de ventes basé sur moyenne mobile"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.data: Optional[pd.DataFrame] = None
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Charge les données de ventes depuis un fichier CSV"""
        self.data = pd.read_csv(filepath, parse_dates=['date'])
        return self.data
    
    def prepare_data_for_prophet(self, product_id: str) -> pd.DataFrame:
        """Prépare les données au format Prophet (ds, y)"""
        if self.data is None:
            raise ValueError("Données non chargées. Appelez load_data() d'abord.")
        
        product_data = self.data[self.data['product_id'] == product_id].copy()
        
        daily_sales = product_data.groupby('date')['quantity'].sum().reset_index()
        daily_sales.columns = ['ds', 'y']
        
        return daily_sales
    
    def train_model(self, product_id: str) -> Dict[str, Any]:
        """Entraîne un modèle Prophet pour un produit spécifique"""
        df = self.prepare_data_for_prophet(product_id)
        
        if len(df) < 14:
            return {
                "success": False,
                "error": "Pas assez de données pour l'entraînement (minimum 14 jours)"
            }
        
        if PROPHET_AVAILABLE:
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )
            model.fit(df)
            self.models[product_id] = model
        
        return {
            "success": True,
            "product_id": product_id,
            "training_samples": len(df),
            "date_range": {
                "start": df['ds'].min().strftime('%Y-%m-%d'),
                "end": df['ds'].max().strftime('%Y-%m-%d')
            }
        }
    
    def predict(self, product_id: str, days: int = 30) -> Dict[str, Any]:
        """Génère des prédictions pour les N prochains jours"""
        df = self.prepare_data_for_prophet(product_id)
        
        if PROPHET_AVAILABLE and product_id in self.models:
            model = self.models[product_id]
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            
            predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
            
            return {
                "product_id": product_id,
                "predictions": [
                    {
                        "date": row['ds'].strftime('%Y-%m-%d'),
                        "predicted_quantity": max(0, round(row['yhat'])),
                        "lower_bound": max(0, round(row['yhat_lower'])),
                        "upper_bound": max(0, round(row['yhat_upper']))
                    }
                    for _, row in predictions.iterrows()
                ]
            }
        else:
            return self._fallback_prediction(df, product_id, days)
    
    def _fallback_prediction(self, df: pd.DataFrame, product_id: str, days: int) -> Dict[str, Any]:
        """Prédiction simple basée sur la moyenne mobile (fallback si Prophet non disponible)"""
        recent_data = df.tail(14)
        mean_sales = recent_data['y'].mean()
        std_sales = recent_data['y'].std()
        
        last_date = df['ds'].max()
        
        predictions = []
        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)
            day_of_week = pred_date.weekday()
            
            if day_of_week in [5, 6]:
                multiplier = 1.3
            else:
                multiplier = 1.0
            
            predicted = mean_sales * multiplier
            
            predictions.append({
                "date": pred_date.strftime('%Y-%m-%d'),
                "predicted_quantity": max(0, round(predicted)),
                "lower_bound": max(0, round(predicted - std_sales)),
                "upper_bound": max(0, round(predicted + std_sales))
            })
        
        return {
            "product_id": product_id,
            "method": "moving_average_fallback",
            "predictions": predictions
        }
    
    def get_sales_summary(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Retourne un résumé des ventes"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        if product_id:
            data = self.data[self.data['product_id'] == product_id]
        else:
            data = self.data
        
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
    
    def get_products(self) -> List[Dict[str, Any]]:
        """Retourne la liste des produits disponibles"""
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
    
    def get_daily_sales(self, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retourne les ventes journalières"""
        if self.data is None:
            raise ValueError("Données non chargées")
        
        if product_id:
            data = self.data[self.data['product_id'] == product_id]
        else:
            data = self.data
        
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
