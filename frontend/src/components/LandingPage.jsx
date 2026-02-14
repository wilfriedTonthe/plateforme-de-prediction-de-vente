import { useState } from 'react'
import { 
  TrendingUp, 
  Globe, 
  Upload, 
  BarChart3, 
  Brain, 
  Calendar,
  Shield,
  Zap,
  Users,
  CheckCircle,
  ArrowRight,
  MapPin
} from 'lucide-react'

const REGIONS = [
  {
    name: "Europe",
    countries: ["France", "Allemagne", "Italie", "Espagne", "Royaume-Uni", "Belgique", "Suisse", "Pays-Bas", "Portugal", "Autriche", "Turquie"]
  },
  {
    name: "Amérique du Nord",
    countries: ["États-Unis", "Canada", "Mexique"]
  },
  {
    name: "Amérique du Sud",
    countries: ["Brésil", "Argentine", "Colombie", "Chili"]
  },
  {
    name: "Afrique",
    countries: ["Maroc", "Algérie", "Tunisie", "Égypte", "Afrique du Sud"]
  },
  {
    name: "Asie",
    countries: ["Japon", "Chine", "Corée du Sud", "Inde", "Singapour", "Hong Kong", "Taiwan"]
  },
  {
    name: "Moyen-Orient",
    countries: ["Émirats Arabes Unis", "Arabie Saoudite", "Israël"]
  },
  {
    name: "Océanie",
    countries: ["Australie", "Nouvelle-Zélande"]
  }
]

const FEATURES = [
  {
    icon: <Upload className="w-8 h-8" />,
    title: "Import Intelligent",
    description: "Importez vos données CSV/Excel avec détection automatique des colonnes (date, quantité, produit, prix)"
  },
  {
    icon: <Brain className="w-8 h-8" />,
    title: "AutoML Avancé",
    description: "5 modèles ML testés automatiquement (XGBoost, Random Forest, Gradient Boosting, Ridge, Linear) - le meilleur est sélectionné"
  },
  {
    icon: <Globe className="w-8 h-8" />,
    title: "Enrichissement Géographique",
    description: "Prédictions ajustées selon les jours fériés de votre pays (34+ pays supportés)"
  },
  {
    icon: <BarChart3 className="w-8 h-8" />,
    title: "Explications Détaillées",
    description: "Comprenez vos prédictions avec des analyses de tendance, facteurs clés et recommandations"
  },
  {
    icon: <Calendar className="w-8 h-8" />,
    title: "Calendrier des Fériés",
    description: "Visualisez les jours fériés de votre région et leur impact sur les ventes"
  },
  {
    icon: <Zap className="w-8 h-8" />,
    title: "Prédictions Rapides",
    description: "Obtenez des prévisions de 7 à 60 jours en quelques secondes"
  }
]

const STEPS = [
  {
    number: "1",
    title: "Sélectionnez votre pays",
    description: "Choisissez votre localisation pour des prédictions adaptées aux jours fériés locaux"
  },
  {
    number: "2",
    title: "Importez vos données",
    description: "Glissez-déposez votre fichier CSV ou utilisez les données de démonstration"
  },
  {
    number: "3",
    title: "Lancez la prédiction",
    description: "Notre IA analyse vos données et génère des prévisions précises"
  },
  {
    number: "4",
    title: "Analysez les résultats",
    description: "Consultez les graphiques, explications et recommandations"
  }
]

function LandingPage({ onStart }) {
  const [selectedRegion, setSelectedRegion] = useState(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10"></div>
        
        <div className="max-w-7xl mx-auto px-4 py-16 sm:py-24 relative z-10">
          <div className="text-center">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="bg-blue-500 p-3 rounded-2xl">
                <TrendingUp className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-4xl sm:text-5xl font-bold text-white">
                SalesPredict <span className="text-blue-400">AI</span>
              </h1>
            </div>
            
            <p className="text-xl sm:text-2xl text-blue-200 mb-4 max-w-3xl mx-auto">
              Plateforme de prédiction de ventes intelligente
            </p>
            <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
              Utilisez l'intelligence artificielle pour anticiper vos ventes, 
              optimiser votre stock et prendre des décisions éclairées.
              <strong className="text-white"> Disponible dans le monde entier.</strong>
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <button
                onClick={onStart}
                className="px-8 py-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl transition-all transform hover:scale-105 flex items-center gap-2 shadow-lg shadow-blue-500/30"
              >
                Commencer maintenant
                <ArrowRight className="w-5 h-5" />
              </button>
              <a
                href="#features"
                className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl transition-all border border-white/20"
              >
                En savoir plus
              </a>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-3xl mx-auto">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <p className="text-3xl font-bold text-white">34+</p>
                <p className="text-blue-200 text-sm">Pays supportés</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <p className="text-3xl font-bold text-white">5</p>
                <p className="text-blue-200 text-sm">Modèles ML</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <p className="text-3xl font-bold text-white">100%</p>
                <p className="text-blue-200 text-sm">Gratuit</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                <p className="text-3xl font-bold text-white">24/7</p>
                <p className="text-blue-200 text-sm">Disponible</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section id="features" className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Fonctionnalités Puissantes
            </h2>
            <p className="text-slate-300 max-w-2xl mx-auto">
              Une suite complète d'outils pour prédire vos ventes avec précision
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {FEATURES.map((feature, idx) => (
              <div 
                key={idx}
                className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700 hover:border-blue-500/50 transition-all hover:transform hover:scale-105"
              >
                <div className="bg-blue-500/20 w-16 h-16 rounded-xl flex items-center justify-center text-blue-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 bg-slate-900">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Comment ça marche ?
            </h2>
            <p className="text-slate-300 max-w-2xl mx-auto">
              En 4 étapes simples, obtenez des prédictions précises pour votre business
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((step, idx) => (
              <div key={idx} className="relative">
                <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 h-full">
                  <div className="bg-blue-500 w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xl mb-4">
                    {step.number}
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-slate-400 text-sm">{step.description}</p>
                </div>
                {idx < STEPS.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="w-8 h-8 text-blue-500/50" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Countries Section */}
      <section className="py-20 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Globe className="w-8 h-8 text-blue-400" />
              <h2 className="text-3xl sm:text-4xl font-bold text-white">
                Disponible Partout dans le Monde
              </h2>
            </div>
            <p className="text-slate-300 max-w-2xl mx-auto">
              Nos prédictions s'adaptent aux jours fériés et spécificités de chaque pays
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {REGIONS.map((region, idx) => (
              <div 
                key={idx}
                className={`bg-slate-800/50 rounded-xl p-4 border cursor-pointer transition-all ${
                  selectedRegion === idx 
                    ? 'border-blue-500 bg-blue-500/10' 
                    : 'border-slate-700 hover:border-slate-600'
                }`}
                onClick={() => setSelectedRegion(selectedRegion === idx ? null : idx)}
              >
                <div className="flex items-center gap-2 mb-3">
                  <MapPin className="w-5 h-5 text-blue-400" />
                  <h3 className="font-semibold text-white">{region.name}</h3>
                </div>
                <div className="flex flex-wrap gap-1">
                  {region.countries.map((country, cidx) => (
                    <span 
                      key={cidx}
                      className="px-2 py-1 bg-slate-700/50 text-slate-300 text-xs rounded-full"
                    >
                      {country}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-8">
            <p className="text-slate-400">
              <CheckCircle className="w-5 h-5 inline mr-2 text-green-400" />
              Jours fériés automatiquement pris en compte dans les prédictions
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Prêt à prédire vos ventes ?
          </h2>
          <p className="text-blue-100 mb-8 text-lg">
            Commencez gratuitement dès maintenant. Aucune inscription requise.
          </p>
          <button
            onClick={onStart}
            className="px-10 py-4 bg-white text-blue-600 font-semibold rounded-xl transition-all transform hover:scale-105 flex items-center gap-2 mx-auto shadow-xl"
          >
            <TrendingUp className="w-5 h-5" />
            Lancer l'application
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-slate-900 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-blue-400" />
              <span className="text-white font-semibold">SalesPredict AI</span>
            </div>
            <p className="text-slate-400 text-sm">
              Plateforme de prédiction de ventes propulsée par l'IA
            </p>
            <div className="flex items-center gap-4 text-slate-400 text-sm">
              <span>© 2024</span>
              <span>•</span>
              <span>Open Source</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
