import { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  Package, 
  DollarSign, 
  BarChart3, 
  RefreshCw,
  Calendar,
  ArrowUp,
  ArrowDown,
  Loader2,
  Upload,
  Download,
  RotateCcw
} from 'lucide-react'
import FileUpload from './components/FileUpload'
import LandingPage from './components/LandingPage'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api'

function App() {
  const [products, setProducts] = useState([])
  const [summary, setSummary] = useState(null)
  const [dailySales, setDailySales] = useState([])
  const [predictions, setPredictions] = useState([])
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [predicting, setPredicting] = useState(false)
  const [predictionDays, setPredictionDays] = useState(14)
  const [showUpload, setShowUpload] = useState(false)
  const [dataSource, setDataSource] = useState('demo')
  const [explanation, setExplanation] = useState(null)
  const [modelUsed, setModelUsed] = useState(null)
  const [countries, setCountries] = useState([])
  const [selectedCountry, setSelectedCountry] = useState('FR')
  const [holidays, setHolidays] = useState([])
  const [showLanding, setShowLanding] = useState(true)

  useEffect(() => {
    loadInitialData()
    loadCountries()
  }, [])

  const loadInitialData = async () => {
    setLoading(true)
    try {
      const [productsRes, summaryRes, salesRes] = await Promise.all([
        axios.get(`${API_BASE}/products`),
        axios.get(`${API_BASE}/summary`),
        axios.get(`${API_BASE}/sales/daily`)
      ])
      
      setProducts(productsRes.data.data)
      setSummary(summaryRes.data.data)
      setDailySales(salesRes.data.data)
      
      if (productsRes.data.data.length > 0) {
        setSelectedProduct(productsRes.data.data[0].product_id)
      }
    } catch (error) {
      console.error('Erreur lors du chargement:', error)
    }
    setLoading(false)
  }

  const loadCountries = async () => {
    try {
      const res = await axios.get(`${API_BASE}/countries`)
      setCountries(res.data.data)
    } catch (error) {
      console.error('Erreur chargement pays:', error)
    }
  }

  const loadHolidays = async (countryCode) => {
    try {
      const res = await axios.get(`${API_BASE}/holidays/${countryCode}?days=${predictionDays}`)
      setHolidays(res.data.data)
    } catch (error) {
      console.error('Erreur chargement jours fériés:', error)
    }
  }

  const handleDataLoaded = (result) => {
    setShowUpload(false)
    setDataSource('import')
    setPredictions([])
    loadInitialData()
  }

  const handleResetData = async () => {
    try {
      await axios.post(`${API_BASE}/reset`)
      setDataSource('demo')
      setPredictions([])
      loadInitialData()
    } catch (error) {
      console.error('Erreur:', error)
    }
  }

  const handleExportPredictions = () => {
    if (selectedProduct && predictions.length > 0) {
      window.open(`${API_BASE}/export/predictions/${selectedProduct}?days=${predictionDays}`, '_blank')
    }
  }

  const loadProductData = async (productId) => {
    try {
      const salesRes = await axios.get(`${API_BASE}/sales/daily/${productId}`)
      setDailySales(salesRes.data.data)
    } catch (error) {
      console.error('Erreur:', error)
    }
  }

  const handleProductChange = (productId) => {
    setSelectedProduct(productId)
    setPredictions([])
    loadProductData(productId)
  }

  const generatePredictions = async () => {
    if (!selectedProduct) return
    
    setPredicting(true)
    setExplanation(null)
    setModelUsed(null)
    setHolidays([])
    try {
      await axios.post(`${API_BASE}/train/${selectedProduct}`)
      
      const predRes = await axios.get(
        `${API_BASE}/predict/${selectedProduct}/geo?days=${predictionDays}&country=${selectedCountry}`
      )
      setPredictions(predRes.data.data.predictions)
      setExplanation(predRes.data.data.explanation)
      setModelUsed(predRes.data.data.model_used)
      setHolidays(predRes.data.data.holidays_in_period || [])
    } catch (error) {
      console.error('Erreur de prédiction:', error)
    }
    setPredicting(false)
  }

  const COUNTRY_CURRENCIES = {
    FR: { currency: 'EUR', locale: 'fr-FR' },
    DE: { currency: 'EUR', locale: 'de-DE' },
    IT: { currency: 'EUR', locale: 'it-IT' },
    ES: { currency: 'EUR', locale: 'es-ES' },
    GB: { currency: 'GBP', locale: 'en-GB' },
    BE: { currency: 'EUR', locale: 'fr-BE' },
    CH: { currency: 'CHF', locale: 'fr-CH' },
    NL: { currency: 'EUR', locale: 'nl-NL' },
    PT: { currency: 'EUR', locale: 'pt-PT' },
    AT: { currency: 'EUR', locale: 'de-AT' },
    US: { currency: 'USD', locale: 'en-US' },
    CA: { currency: 'CAD', locale: 'en-CA' },
    BR: { currency: 'BRL', locale: 'pt-BR' },
    MX: { currency: 'MXN', locale: 'es-MX' },
    AR: { currency: 'ARS', locale: 'es-AR' },
    CO: { currency: 'COP', locale: 'es-CO' },
    CL: { currency: 'CLP', locale: 'es-CL' },
    MA: { currency: 'MAD', locale: 'fr-MA' },
    ZA: { currency: 'ZAR', locale: 'en-ZA' },
    DZ: { currency: 'DZD', locale: 'fr-DZ' },
    TN: { currency: 'TND', locale: 'fr-TN' },
    EG: { currency: 'EGP', locale: 'ar-EG' },
    JP: { currency: 'JPY', locale: 'ja-JP' },
    CN: { currency: 'CNY', locale: 'zh-CN' },
    KR: { currency: 'KRW', locale: 'ko-KR' },
    IN: { currency: 'INR', locale: 'en-IN' },
    SG: { currency: 'SGD', locale: 'en-SG' },
    HK: { currency: 'HKD', locale: 'zh-HK' },
    TW: { currency: 'TWD', locale: 'zh-TW' },
    AU: { currency: 'AUD', locale: 'en-AU' },
    NZ: { currency: 'NZD', locale: 'en-NZ' },
    TR: { currency: 'TRY', locale: 'tr-TR' },
    AE: { currency: 'AED', locale: 'ar-AE' },
    SA: { currency: 'SAR', locale: 'ar-SA' },
    IL: { currency: 'ILS', locale: 'he-IL' },
  }

  const formatCurrency = (value) => {
    const countryConfig = COUNTRY_CURRENCIES[selectedCountry] || { currency: 'EUR', locale: 'fr-FR' }
    return new Intl.NumberFormat(countryConfig.locale, {
      style: 'currency',
      currency: countryConfig.currency
    }).format(value)
  }

  const formatNumber = (value) => {
    return new Intl.NumberFormat('fr-FR').format(value)
  }

  const combinedChartData = [
    ...dailySales.map(d => ({ ...d, type: 'actual' })),
    ...predictions.map(p => ({
      date: p.date,
      quantity: p.predicted_quantity,
      lower: p.lower_bound,
      upper: p.upper_bound,
      type: 'prediction'
    }))
  ]

  if (showLanding) {
    return <LandingPage onStart={() => setShowLanding(false)} />
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto" />
          <p className="mt-4 text-slate-600">Chargement des données...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">SalesPredict AI</h1>
                <p className="text-sm text-slate-500">
                  Prédiction de ventes par IA
                  {dataSource === 'import' && (
                    <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                      Données importées
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowUpload(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Upload className="w-4 h-4" />
                Importer CSV
              </button>
              {dataSource === 'import' && (
                <button
                  onClick={handleResetData}
                  className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                  title="Réinitialiser avec les données de démo"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={loadInitialData}
                className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {showUpload && (
        <FileUpload 
          onDataLoaded={handleDataLoaded} 
          onClose={() => setShowUpload(false)} 
        />
      )}

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <StatCard
              title="Chiffre d'affaires"
              value={formatCurrency(summary.total_sales)}
              icon={<DollarSign className="w-5 h-5" />}
              color="green"
            />
            <StatCard
              title="Quantité vendue"
              value={formatNumber(summary.total_quantity)}
              icon={<Package className="w-5 h-5" />}
              color="blue"
            />
            <StatCard
              title="Moyenne journalière"
              value={formatNumber(Math.round(summary.average_daily_quantity))}
              icon={<BarChart3 className="w-5 h-5" />}
              color="purple"
            />
            <StatCard
              title="Produits"
              value={summary.products}
              icon={<TrendingUp className="w-5 h-5" />}
              color="orange"
            />
          </div>
        )}

        {/* Product Selection & Prediction Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">
            Prédiction de ventes
          </h2>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Produit
              </label>
              <select
                value={selectedProduct || ''}
                onChange={(e) => handleProductChange(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {products.map((product) => (
                  <option key={product.product_id} value={product.product_id}>
                    {product.product_name} ({product.category})
                  </option>
                ))}
              </select>
            </div>
            <div className="w-32">
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Jours
              </label>
              <select
                value={predictionDays}
                onChange={(e) => setPredictionDays(Number(e.target.value))}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value={7}>7 jours</option>
                <option value={14}>14 jours</option>
                <option value={30}>30 jours</option>
                <option value={60}>60 jours</option>
              </select>
            </div>
            <div className="w-48">
              <label className="block text-sm font-medium text-slate-600 mb-2">
                Pays / Région
              </label>
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {countries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={generatePredictions}
              disabled={predicting || !selectedProduct}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              {predicting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Calcul...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4" />
                  Prédire
                </>
              )}
            </button>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Sales History Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">
              Historique des ventes
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={dailySales}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => value.slice(5)}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#fff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="quantity"
                    stroke="#3b82f6"
                    fill="#93c5fd"
                    name="Quantité"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Predictions Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">
                Prédictions
                {predictions.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-slate-500">
                    ({predictions.length} jours)
                  </span>
                )}
              </h3>
              {predictions.length > 0 && (
                <button
                  onClick={handleExportPredictions}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Exporter CSV
                </button>
              )}
            </div>
            <div className="h-80">
              {predictions.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={predictions}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => value.slice(5)}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#fff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="predicted_quantity"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ fill: '#10b981' }}
                      name="Prédiction"
                    />
                    <Line
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="#94a3b8"
                      strokeDasharray="5 5"
                      dot={false}
                      name="Limite haute"
                    />
                    <Line
                      type="monotone"
                      dataKey="lower_bound"
                      stroke="#94a3b8"
                      strokeDasharray="5 5"
                      dot={false}
                      name="Limite basse"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-slate-400">
                  <div className="text-center">
                    <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Sélectionnez un produit et cliquez sur "Prédire"</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Explanation Panel */}
        {explanation && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">
                Analyse des Prédictions
              </h3>
              {modelUsed && (
                <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm font-medium rounded-full">
                  Modèle: {modelUsed}
                </span>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500 mb-1">Prévision moyenne</p>
                <p className="text-2xl font-bold text-slate-800">
                  {explanation.statistics?.average_prediction} <span className="text-sm font-normal">unités/jour</span>
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500 mb-1">Tendance</p>
                <p className={`text-2xl font-bold ${
                  explanation.trend?.direction === 'hausse' ? 'text-green-600' :
                  explanation.trend?.direction === 'baisse' ? 'text-red-600' : 'text-slate-800'
                }`}>
                  {explanation.trend?.direction === 'hausse' ? '↑' : 
                   explanation.trend?.direction === 'baisse' ? '↓' : '→'} {explanation.trend?.direction}
                  {explanation.trend?.percentage > 0 && ` (${explanation.trend?.percentage}%)`}
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500 mb-1">Confiance</p>
                <p className={`text-2xl font-bold ${
                  explanation.model_info?.confidence === 'elevee' ? 'text-green-600' :
                  explanation.model_info?.confidence === 'moyenne' ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {explanation.model_info?.confidence}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-700 mb-3">Facteurs clés</h4>
                <div className="space-y-2">
                  {explanation.factors?.map((factor, idx) => (
                    <div key={idx} className="flex items-start gap-2 p-2 bg-slate-50 rounded-lg">
                      <span className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${
                        factor.impact === 'positif' ? 'bg-green-500' :
                        factor.impact === 'negatif' ? 'bg-red-500' : 'bg-slate-400'
                      }`}></span>
                      <div>
                        <p className="font-medium text-slate-700 text-sm">{factor.factor}</p>
                        <p className="text-xs text-slate-500">{factor.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-slate-700 mb-3">Recommandations</h4>
                <ul className="space-y-2">
                  {explanation.recommendations?.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                      <span className="text-blue-500 mt-0.5">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-xs text-slate-500">Meilleur jour</p>
                <p className="font-medium text-green-600">{explanation.key_days?.best_day?.day_name}</p>
                <p className="text-sm text-slate-600">{explanation.key_days?.best_day?.quantity} unités</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Jour le plus faible</p>
                <p className="font-medium text-red-600">{explanation.key_days?.worst_day?.day_name}</p>
                <p className="text-sm text-slate-600">{explanation.key_days?.worst_day?.quantity} unités</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Moyenne weekend</p>
                <p className="font-medium text-slate-800">{explanation.statistics?.weekend_average}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Moyenne semaine</p>
                <p className="font-medium text-slate-800">{explanation.statistics?.weekday_average}</p>
              </div>
            </div>

            {/* Jours fériés */}
            {holidays.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-200">
                <h4 className="font-medium text-slate-700 mb-3">
                  Jours fériés dans la période ({countries.find(c => c.code === selectedCountry)?.name})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {holidays.map((holiday, idx) => (
                    <span 
                      key={idx}
                      className="px-3 py-1 bg-orange-100 text-orange-700 text-sm rounded-full"
                    >
                      {holiday.name} - {holiday.date}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Products Table */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800">
              Produits
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Produit
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Catégorie
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Prix unitaire
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Quantité vendue
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Chiffre d'affaires
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {products.map((product) => (
                  <tr 
                    key={product.product_id}
                    className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                      selectedProduct === product.product_id ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => handleProductChange(product.product_id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                          <Package className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium text-slate-800">
                            {product.product_name}
                          </div>
                          <div className="text-sm text-slate-500">
                            {product.product_id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-3 py-1 text-xs font-medium bg-slate-100 text-slate-700 rounded-full">
                        {product.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-slate-600">
                      {formatCurrency(product.unit_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-slate-800">
                      {formatNumber(product.total_quantity_sold)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right font-medium text-green-600">
                      {formatCurrency(product.total_revenue)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Predictions Table */}
        {predictions.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-6">
            <div className="px-6 py-4 border-b border-slate-200">
              <h3 className="text-lg font-semibold text-slate-800">
                Détail des prédictions
              </h3>
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full">
                <thead className="bg-slate-50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Quantité prédite
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Limite basse
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Limite haute
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {predictions.map((pred, index) => (
                    <tr key={index} className="hover:bg-slate-50">
                      <td className="px-6 py-3 whitespace-nowrap text-slate-800">
                        {new Date(pred.date).toLocaleDateString('fr-FR', {
                          weekday: 'short',
                          day: 'numeric',
                          month: 'short'
                        })}
                      </td>
                      <td className="px-6 py-3 whitespace-nowrap text-right font-medium text-green-600">
                        {pred.predicted_quantity}
                      </td>
                      <td className="px-6 py-3 whitespace-nowrap text-right text-slate-500">
                        {pred.lower_bound}
                      </td>
                      <td className="px-6 py-3 whitespace-nowrap text-right text-slate-500">
                        {pred.upper_bound}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-slate-500">
          Sales Prediction v1.0 - Prédiction de ventes par IA
        </div>
      </footer>
    </div>
  )
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    green: 'bg-green-100 text-green-600',
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600'
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

export default App
