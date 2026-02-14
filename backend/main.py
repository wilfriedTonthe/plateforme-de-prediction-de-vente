from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import io
import pandas as pd

from automl_model import AutoMLPredictor
from csv_detector import CSVColumnDetector, detect_csv_structure
from geo_enrichment import geo_enrichment, SUPPORTED_COUNTRIES

app = FastAPI(
    title="Sales Prediction API",
    description="API de prédiction de ventes basée sur l'IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prediction_model = AutoMLPredictor()

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sales_data.csv")


class PredictionRequest(BaseModel):
    product_id: str
    days: int = 30


class TrainRequest(BaseModel):
    product_id: str


@app.on_event("startup")
async def startup_event():
    """Charge les données au démarrage"""
    try:
        prediction_model.load_data(DATA_PATH)
        print(f"[OK] Donnees chargees depuis {DATA_PATH}")
    except Exception as e:
        print(f"[ERREUR] Erreur lors du chargement des donnees: {e}")


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Sales Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "summary": "/api/summary",
            "daily_sales": "/api/sales/daily",
            "predict": "/api/predict/{product_id}",
            "train": "/api/train/{product_id}",
            "upload": "/api/upload",
            "detect": "/api/detect-columns",
            "export": "/api/export/predictions/{product_id}"
        }
    }


@app.get("/api/products")
async def get_products():
    """Retourne la liste des produits"""
    try:
        products = prediction_model.get_products()
        return {"success": True, "data": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
async def get_summary(product_id: Optional[str] = None):
    """Retourne un résumé des ventes"""
    try:
        summary = prediction_model.get_sales_summary(product_id)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/daily")
async def get_daily_sales(product_id: Optional[str] = None):
    """Retourne les ventes journalières"""
    try:
        sales = prediction_model.get_daily_sales(product_id)
        return {"success": True, "data": sales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/daily/{product_id}")
async def get_daily_sales_by_product(product_id: str):
    """Retourne les ventes journalières pour un produit"""
    try:
        sales = prediction_model.get_daily_sales(product_id)
        return {"success": True, "data": sales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/train/{product_id}")
async def train_model(product_id: str):
    """Entraîne le modèle AutoML pour un produit (sélection automatique du meilleur modèle)"""
    try:
        result = prediction_model.train_and_select_best(product_id)
        if result["success"]:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erreur inconnue"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predict/{product_id}")
async def predict(product_id: str, days: int = 30):
    """Génère des prédictions pour un produit"""
    try:
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Le nombre de jours doit être entre 1 et 365")
        
        predictions = prediction_model.predict(product_id, days)
        return {"success": True, "data": predictions}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Vérifie l'état de l'API"""
    return {
        "status": "healthy",
        "data_loaded": prediction_model.data is not None,
        "models_trained": len(prediction_model.models)
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload un fichier CSV et détecte automatiquement sa structure"""
    try:
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Format non supporté. Utilisez CSV ou Excel."
            )
        
        contents = await file.read()
        
        detector = CSVColumnDetector()
        
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        detection = detector.detect_from_dataframe(df)
        
        return {
            "success": True,
            "filename": file.filename,
            "detection": detection
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/load-data")
async def load_uploaded_data(
    file: UploadFile = File(...),
    date_column: str = None,
    quantity_column: str = None,
    product_column: Optional[str] = None
):
    """Charge les données uploadées pour la prédiction"""
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        detector = CSVColumnDetector()
        detector.df = df
        detection = detector._analyze_columns()
        
        if not date_column:
            date_column = detection["detected"].get("date")
        if not quantity_column:
            quantity_column = detection["detected"].get("quantity")
        if not product_column:
            product_column = detection["detected"].get("product")
        
        if not date_column or not quantity_column:
            raise HTTPException(
                status_code=400,
                detail="Impossible de détecter les colonnes date et quantité"
            )
        
        prepared_df = detector.prepare_data_for_prediction(
            date_column, quantity_column, product_column
        )
        
        if product_column and product_column in df.columns:
            prepared_df['category'] = 'Import'
            prepared_df['unit_price'] = 0
            prepared_df['total_sales'] = prepared_df['quantity']
            prepared_df = prepared_df.rename(columns={'quantity': 'quantity'})
        
        prediction_model.data = prepared_df.rename(columns={
            'date': 'date',
            'quantity': 'quantity', 
            'product_id': 'product_id',
            'product_name': 'product_name'
        })
        prediction_model.data['category'] = 'Import'
        prediction_model.data['unit_price'] = 0
        prediction_model.data['total_sales'] = prediction_model.data['quantity']
        
        return {
            "success": True,
            "message": "Données chargées avec succès",
            "rows": len(prediction_model.data),
            "products": prediction_model.data['product_id'].nunique(),
            "columns_used": {
                "date": date_column,
                "quantity": quantity_column,
                "product": product_column
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/detect-columns")
async def detect_columns(file: UploadFile = File(...)):
    """Détecte les colonnes d'un fichier CSV sans le charger"""
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        detector = CSVColumnDetector()
        detection = detector.detect_from_dataframe(df)
        
        return {"success": True, "detection": detection}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/predictions/{product_id}")
async def export_predictions(product_id: str, days: int = 30):
    """Exporte les prédictions au format CSV"""
    try:
        predictions = prediction_model.predict(product_id, days)
        
        df = pd.DataFrame(predictions["predictions"])
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=predictions_{product_id}_{days}days.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset_data():
    """Réinitialise les données avec le fichier de démo"""
    try:
        prediction_model.load_data(DATA_PATH)
        prediction_model.models = {}
        return {"success": True, "message": "Données réinitialisées"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== ENDPOINTS GEOGRAPHIQUES ==============

@app.get("/api/countries")
async def get_countries():
    """Retourne la liste des pays supportés"""
    countries = geo_enrichment.get_supported_countries()
    return {"success": True, "data": countries}


@app.get("/api/country/{country_code}")
async def get_country_info(country_code: str):
    """Retourne les informations d'un pays"""
    country_code = country_code.upper()
    info = geo_enrichment.get_country_info(country_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"Pays non supporté: {country_code}")
    return {"success": True, "data": info}


@app.get("/api/holidays/{country_code}")
async def get_holidays(country_code: str, days: int = 90):
    """Retourne les jours fériés à venir pour un pays"""
    country_code = country_code.upper()
    if country_code not in SUPPORTED_COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Pays non supporté: {country_code}")
    
    holidays = geo_enrichment.get_upcoming_holidays(country_code, days)
    return {
        "success": True,
        "country": country_code,
        "data": holidays
    }


@app.get("/api/predict/{product_id}/geo")
async def predict_with_geo(product_id: str, days: int = 30, country: str = "FR"):
    """Génère des prédictions avec enrichissement géographique"""
    try:
        country = country.upper()
        if country not in SUPPORTED_COUNTRIES:
            raise HTTPException(status_code=400, detail=f"Pays non supporté: {country}")
        
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Le nombre de jours doit être entre 1 et 365")
        
        base_predictions = prediction_model.predict(product_id, days)
        
        from datetime import datetime
        enriched_predictions = []
        for pred in base_predictions.get("predictions", []):
            pred_date = datetime.strptime(pred["date"], '%Y-%m-%d').date()
            
            multiplier = geo_enrichment.get_holiday_impact_multiplier(country, pred_date)
            geo_features = geo_enrichment.enrich_date_features(country, pred_date)
            
            adjusted_qty = round(pred["predicted_quantity"] * multiplier)
            adjusted_lower = round(pred["lower_bound"] * multiplier)
            adjusted_upper = round(pred["upper_bound"] * multiplier)
            
            enriched_predictions.append({
                **pred,
                "predicted_quantity": adjusted_qty,
                "lower_bound": max(0, adjusted_lower),
                "upper_bound": adjusted_upper,
                "original_quantity": pred["predicted_quantity"],
                "holiday_multiplier": multiplier,
                "is_holiday": geo_features["is_holiday"],
                "is_pre_holiday": geo_features["is_pre_holiday"]
            })
        
        country_info = geo_enrichment.get_country_info(country)
        upcoming_holidays = geo_enrichment.get_upcoming_holidays(country, days)
        
        return {
            "success": True,
            "data": {
                "product_id": product_id,
                "model_used": base_predictions.get("model_used", "AutoML"),
                "country": country_info,
                "predictions": enriched_predictions,
                "explanation": base_predictions.get("explanation", {}),
                "holidays_in_period": upcoming_holidays,
                "geo_enrichment": True
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
