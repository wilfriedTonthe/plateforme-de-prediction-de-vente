import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class CSVColumnDetector:
    """Détecte automatiquement les colonnes d'un fichier CSV de ventes"""
    
    DATE_PATTERNS = [
        'date', 'datetime', 'time', 'timestamp', 'jour', 'day',
        'fecha', 'data', 'created_at', 'order_date', 'sale_date'
    ]
    
    QUANTITY_PATTERNS = [
        'quantity', 'qty', 'quantite', 'quantité', 'amount', 'count',
        'units', 'volume', 'nb', 'nombre', 'ventes', 'sales', 'sold'
    ]
    
    PRODUCT_PATTERNS = [
        'product', 'produit', 'item', 'article', 'sku', 'product_name',
        'product_id', 'nom_produit', 'item_name', 'name'
    ]
    
    CATEGORY_PATTERNS = [
        'category', 'categorie', 'catégorie', 'type', 'group', 'famille',
        'category_name', 'product_category', 'cat'
    ]
    
    PRICE_PATTERNS = [
        'price', 'prix', 'unit_price', 'prix_unitaire', 'cost', 'amount',
        'total', 'revenue', 'total_sales', 'montant', 'ca', 'chiffre'
    ]
    
    def __init__(self):
        self.detected_columns: Dict[str, str] = {}
        self.df: Optional[pd.DataFrame] = None
        
    def detect_from_file(self, filepath: str) -> Dict[str, Any]:
        """Détecte les colonnes depuis un fichier"""
        try:
            if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
                self.df = pd.read_excel(filepath)
            else:
                self.df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            self.df = pd.read_csv(filepath, encoding='latin-1')
        
        return self._analyze_columns()
    
    def detect_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Détecte les colonnes depuis un DataFrame"""
        self.df = df
        return self._analyze_columns()
    
    def _analyze_columns(self) -> Dict[str, Any]:
        """Analyse les colonnes du DataFrame"""
        if self.df is None:
            raise ValueError("Aucune donnée chargée")
        
        columns = list(self.df.columns)
        detection_result = {
            "columns": columns,
            "row_count": len(self.df),
            "detected": {},
            "confidence": {},
            "sample_data": self._safe_sample_data()
        }
        
        detection_result["detected"]["date"] = self._detect_date_column(columns)
        detection_result["detected"]["quantity"] = self._detect_quantity_column(columns)
        detection_result["detected"]["product"] = self._detect_product_column(columns)
        detection_result["detected"]["category"] = self._detect_category_column(columns)
        detection_result["detected"]["price"] = self._detect_price_column(columns)
        
        for col_type, col_name in detection_result["detected"].items():
            if col_name:
                detection_result["confidence"][col_type] = self._calculate_confidence(col_type, col_name)
        
        return detection_result
    
    def _detect_date_column(self, columns: List[str]) -> Optional[str]:
        """Détecte la colonne de date"""
        for col in columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.DATE_PATTERNS):
                return col
        
        for col in columns:
            try:
                sample = self.df[col].dropna().head(10)
                if len(sample) > 0:
                    pd.to_datetime(sample)
                    return col
            except (ValueError, TypeError):
                continue
        
        return None
    
    def _detect_quantity_column(self, columns: List[str]) -> Optional[str]:
        """Détecte la colonne de quantité"""
        for col in columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.QUANTITY_PATTERNS):
                if self._is_numeric_column(col):
                    return col
        
        numeric_cols = [col for col in columns if self._is_numeric_column(col)]
        for col in numeric_cols:
            if self.df[col].dtype in ['int64', 'int32'] and self.df[col].min() >= 0:
                return col
        
        return numeric_cols[0] if numeric_cols else None
    
    def _detect_product_column(self, columns: List[str]) -> Optional[str]:
        """Détecte la colonne produit"""
        for col in columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.PRODUCT_PATTERNS):
                return col
        return None
    
    def _detect_category_column(self, columns: List[str]) -> Optional[str]:
        """Détecte la colonne catégorie"""
        for col in columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.CATEGORY_PATTERNS):
                return col
        return None
    
    def _detect_price_column(self, columns: List[str]) -> Optional[str]:
        """Détecte la colonne prix"""
        for col in columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.PRICE_PATTERNS):
                if self._is_numeric_column(col):
                    return col
        return None
    
    def _is_numeric_column(self, col: str) -> bool:
        """Vérifie si une colonne est numérique"""
        try:
            return pd.api.types.is_numeric_dtype(self.df[col])
        except Exception:
            return False
    
    def _safe_sample_data(self) -> List[Dict[str, Any]]:
        """Retourne les données d'échantillon de manière sécurisée pour JSON"""
        if self.df is None:
            return []
        
        sample_df = self.df.head(5).copy()
        
        for col in sample_df.columns:
            if pd.api.types.is_datetime64_any_dtype(sample_df[col]):
                sample_df[col] = sample_df[col].astype(str)
            elif pd.api.types.is_numeric_dtype(sample_df[col]):
                sample_df[col] = sample_df[col].fillna(0)
            else:
                sample_df[col] = sample_df[col].fillna('').astype(str)
        
        sample_df = sample_df.replace([np.inf, -np.inf], 0)
        
        return sample_df.to_dict(orient='records')
    
    def _calculate_confidence(self, col_type: str, col_name: str) -> float:
        """Calcule un score de confiance pour la détection"""
        col_lower = col_name.lower().strip()
        
        patterns = {
            "date": self.DATE_PATTERNS,
            "quantity": self.QUANTITY_PATTERNS,
            "product": self.PRODUCT_PATTERNS,
            "category": self.CATEGORY_PATTERNS,
            "price": self.PRICE_PATTERNS
        }
        
        if col_type in patterns:
            for pattern in patterns[col_type][:3]:
                if pattern == col_lower:
                    return 1.0
                if pattern in col_lower:
                    return 0.9
            for pattern in patterns[col_type][3:]:
                if pattern in col_lower:
                    return 0.7
        
        return 0.5
    
    def prepare_data_for_prediction(self, date_col: str, quantity_col: str, 
                                     product_col: Optional[str] = None) -> pd.DataFrame:
        """Prépare les données pour la prédiction"""
        if self.df is None:
            raise ValueError("Aucune donnée chargée")
        
        df = self.df.copy()
        
        df['date'] = pd.to_datetime(df[date_col])
        df['quantity'] = pd.to_numeric(df[quantity_col], errors='coerce').fillna(0)
        
        if product_col and product_col in df.columns:
            df['product_id'] = df[product_col].astype(str)
            df['product_name'] = df[product_col].astype(str)
        else:
            df['product_id'] = 'ALL'
            df['product_name'] = 'Tous les produits'
        
        return df[['date', 'quantity', 'product_id', 'product_name']]


def detect_csv_structure(filepath: str) -> Dict[str, Any]:
    """Fonction utilitaire pour détecter la structure d'un CSV"""
    detector = CSVColumnDetector()
    return detector.detect_from_file(filepath)
