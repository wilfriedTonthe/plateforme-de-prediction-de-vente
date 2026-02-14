# SalesPredict AI - Plateforme Universelle de Prediction de Ventes

SalesPredict AI est une application web full-stack permettant d'importer des fichiers de ventes (CSV/Excel) pour generer des previsions automatiques basees sur le Machine Learning, enrichies par des donnees contextuelles geographiques (jours feries par pays).

## Fonctionnalites

- **Import Intelligent** : Detection automatique des colonnes (Date, Ventes, Categories)
- **Drag & Drop** : Interface intuitive pour importer vos fichiers
- **Moteur AutoML** : Selection automatique du meilleur modele (XGBoost, Random Forest, Gradient Boosting, Ridge, Linear)
- **Enrichissement Geographique** : Calendriers de jours feries pour 34+ pays
- **Multi-Devises** : Affichage automatique de la devise selon le pays selectionne
- **Dashboard Interactif** : Visualisation des tendances et predictions avec intervalles de confiance
- **Explications IA** : Recommandations dynamiques basees sur les predictions
- **Export de donnees** : Telechargement des previsions au format CSV

## Architecture Technique

### Backend (Python / FastAPI)

| Composant | Technologie |
|-----------|-------------|
| API | FastAPI (haute performance) |
| Traitement | Pandas, NumPy |
| Modeles IA | XGBoost, Scikit-learn, Statsmodels |
| Enrichissement | Workalendar (jours feries 34+ pays) |

### Frontend (React / Tailwind CSS)

| Composant | Technologie |
|-----------|-------------|
| UI | Tailwind CSS, Lucide Icons |
| Graphiques | Recharts |
| Upload | Drag & Drop natif |

## Structure du Projet

```
sales-prediction/
├── backend/
│   ├── main.py              # API FastAPI + Endpoints
│   ├── automl_model.py      # Moteur AutoML (5 modeles)
│   ├── geo_enrichment.py    # Jours feries par pays
│   ├── csv_detector.py      # Detection auto des colonnes
│   ├── model.py             # Modele legacy
│   ├── requirements.txt
│   └── data/
│       ├── sales_data.csv       # Donnees de demo
│       └── test_sales_data.csv  # Donnees de test
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Dashboard principal
│   │   ├── components/
│   │   │   ├── FileUpload.jsx   # Drag & Drop
│   │   │   └── LandingPage.jsx  # Page d'accueil
│   │   └── ...
│   └── package.json
└── README.md
```

## Installation

### 1. Backend (Python)

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## Format CSV Attendu

La plateforme detecte automatiquement les colonnes. Format recommande :

| date | product_id | product_name | quantity | unit_price | total_sales | category |
|------|------------|--------------|----------|------------|-------------|----------|
| 2024-01-01 | P001 | Laptop HP | 12 | 899.99 | 10799.88 | Electronique |
| 2024-01-02 | P001 | Laptop HP | 8 | 899.99 | 7199.92 | Electronique |

## Utilisation

1. Lancer le backend sur `http://localhost:8001`
2. Lancer le frontend sur `http://localhost:5173`
3. Cliquer sur **Commencer** depuis la page d'accueil
4. Selectionner votre **pays** pour l'enrichissement geographique
5. Choisir un **produit** et cliquer sur **Predire**
6. Consulter les **recommandations** et **explications**

## Pays Supportes

La plateforme supporte les jours feries de 34+ pays :

- **Europe** : France, Allemagne, Italie, Espagne, UK, Belgique, Suisse, Pays-Bas, Portugal, Autriche
- **Amerique du Nord** : USA, Canada
- **Amerique du Sud** : Bresil, Mexique, Argentine, Colombie, Chili
- **Afrique** : Maroc, Afrique du Sud, Algerie, Tunisie, Egypte
- **Asie** : Japon, Chine, Coree du Sud, Inde, Singapour, Hong Kong, Taiwan
- **Oceanie** : Australie, Nouvelle-Zelande
- **Moyen-Orient** : Turquie, Emirats, Arabie Saoudite, Israel

## API Endpoints

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/products` | Liste des produits |
| GET | `/api/summary` | Resume des ventes |
| GET | `/api/sales/daily` | Ventes journalieres |
| POST | `/api/train/{product_id}` | Entrainer le modele AutoML |
| GET | `/api/predict/{product_id}` | Generer des predictions |
| GET | `/api/predict/{product_id}/geo` | Predictions avec enrichissement geo |
| GET | `/api/countries` | Liste des pays supportes |
| GET | `/api/holidays/{country_code}` | Jours feries d'un pays |
| POST | `/api/upload` | Importer un fichier CSV |

## Licence

Distribue sous la licence MIT.
