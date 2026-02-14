# � SalesPredict AI - Plateforme Universelle de Prévision de Ventes

SalesPredict AI est une application web full-stack permettant d'importer des fichiers de ventes (CSV/Excel) pour générer des prévisions automatiques basées sur le Machine Learning, enrichies par des données contextuelles géographiques (météo, jours fériés).

## ✨ Fonctionnalités

- **Import Intelligent** : Détection automatique des colonnes (Date, Ventes, Catégories)
- **Drag & Drop** : Interface intuitive pour importer vos fichiers
- **Moteur AutoML** : Sélection automatique du meilleur modèle (Prophet, XGBoost, ARIMA)
- **Enrichissement Géographique** : Intégration météo et calendriers locaux via API
- **Dashboard Interactif** : Visualisation des tendances et prédictions avec intervalles de confiance
- **Export de données** : Téléchargement des prévisions au format CSV/Excel

## 🏗️ Architecture Technique

### Backend (Python / FastAPI)
| Composant | Technologie |
|-----------|-------------|
| API | FastAPI (haute performance) |
| Traitement | Pandas, NumPy |
| Modèles IA | Prophet, Scikit-learn, XGBoost |
| Enrichissement | Workalendar (jours fériés) |

### Frontend (React / Tailwind CSS)
| Composant | Technologie |
|-----------|-------------|
| UI | Tailwind CSS, Lucide Icons |
| Graphiques | Recharts |
| Upload | Drag & Drop natif |

## 📂 Structure du Projet

```
sales-prediction/
├── backend/
│   ├── main.py           # API FastAPI + Upload
│   ├── model.py          # Moteur de prédiction
│   ├── csv_detector.py   # Détection auto des colonnes
│   ├── requirements.txt
│   └── data/             # Données de démonstration
│       └── sales_data.csv
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Dashboard principal
│   │   ├── components/
│   │   │   └── FileUpload.jsx  # Drag & Drop
│   │   └── ...
│   └── package.json
└── README.md
```

## ⚙️ Installation

### 1. Backend (Python)

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## 📊 Format CSV Attendu

La plateforme détecte automatiquement les colonnes, mais pour des résultats optimaux :

| date | quantity/ventes | product (optionnel) | category (optionnel) |
|------|-----------------|---------------------|----------------------|
| 2024-01-01 | 150 | iPhone 15 | Électronique |
| 2024-01-02 | 120 | MacBook Pro | Électronique |

## 📈 Utilisation

1. Lancer le backend sur `http://localhost:8000`
2. Lancer le frontend sur `http://localhost:5173`
3. **Glisser-déposer** votre fichier CSV ou utiliser les données de démo
4. Sélectionner un produit et générer les prédictions

## 🗺️ Roadmap

- [ ] Support Multi-devises
- [ ] Connexion API Shopify/Amazon/Stripe
- [ ] Analyse What-if (impact promotionnel)
- [ ] Alertes de rupture de stock par email
- [ ] Export Excel avancé

## � Licence

Distribué sous la licence MIT.
