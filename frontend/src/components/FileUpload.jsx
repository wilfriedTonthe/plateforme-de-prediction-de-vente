import { useState, useCallback } from 'react'
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react'
import axios from 'axios'

const API_BASE = '/api'

export default function FileUpload({ onDataLoaded, onClose }) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [detection, setDetection] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [step, setStep] = useState('upload')

  const [dateColumn, setDateColumn] = useState('')
  const [quantityColumn, setQuantityColumn] = useState('')
  const [productColumn, setProductColumn] = useState('')

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      processFile(droppedFile)
    }
  }, [])

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      processFile(selectedFile)
    }
  }

  const processFile = async (selectedFile) => {
    const validExtensions = ['.csv', '.xlsx', '.xls']
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase()
    
    if (!validExtensions.includes(ext)) {
      setError('Format non supporté. Utilisez CSV ou Excel.')
      return
    }

    setFile(selectedFile)
    setError(null)
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (response.data.success) {
        setDetection(response.data.detection)
        
        const detected = response.data.detection.detected
        setDateColumn(detected.date || '')
        setQuantityColumn(detected.quantity || '')
        setProductColumn(detected.product || '')
        
        setStep('configure')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'analyse du fichier')
    }
    
    setLoading(false)
  }

  const handleLoadData = async () => {
    if (!dateColumn || !quantityColumn) {
      setError('Veuillez sélectionner les colonnes date et quantité')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const params = new URLSearchParams()
      params.append('date_column', dateColumn)
      params.append('quantity_column', quantityColumn)
      if (productColumn) {
        params.append('product_column', productColumn)
      }

      const response = await axios.post(
        `${API_BASE}/load-data?${params.toString()}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )

      if (response.data.success) {
        setStep('success')
        setTimeout(() => {
          onDataLoaded && onDataLoaded(response.data)
        }, 1500)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement')
    }

    setLoading(false)
  }

  const resetUpload = () => {
    setFile(null)
    setDetection(null)
    setError(null)
    setStep('upload')
    setDateColumn('')
    setQuantityColumn('')
    setProductColumn('')
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <h2 className="text-xl font-bold text-slate-800">
            {step === 'upload' && 'Importer vos données'}
            {step === 'configure' && 'Configurer les colonnes'}
            {step === 'success' && 'Import réussi'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        <div className="p-6">
          {step === 'upload' && (
            <>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`
                  border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer
                  ${isDragging 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                  }
                `}
                onClick={() => document.getElementById('file-input').click()}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {loading ? (
                  <div className="flex flex-col items-center">
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                    <p className="text-slate-600">Analyse en cours...</p>
                  </div>
                ) : (
                  <>
                    <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-blue-500' : 'text-slate-400'}`} />
                    <p className="text-lg font-medium text-slate-700 mb-2">
                      Glissez-déposez votre fichier ici
                    </p>
                    <p className="text-sm text-slate-500 mb-4">
                      ou cliquez pour sélectionner
                    </p>
                    <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
                      <FileSpreadsheet className="w-4 h-4" />
                      <span>CSV, Excel (.xlsx, .xls)</span>
                    </div>
                  </>
                )}
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </>
          )}

          {step === 'configure' && detection && (
            <>
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <div>
                  <p className="text-green-800 font-medium">{file.name}</p>
                  <p className="text-green-600 text-sm">
                    {detection.row_count} lignes • {detection.columns.length} colonnes
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Colonne Date <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={dateColumn}
                    onChange={(e) => setDateColumn(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionner...</option>
                    {detection.columns.map((col) => (
                      <option key={col} value={col}>
                        {col} {detection.detected.date === col && '(détecté)'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Colonne Quantité/Ventes <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={quantityColumn}
                    onChange={(e) => setQuantityColumn(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionner...</option>
                    {detection.columns.map((col) => (
                      <option key={col} value={col}>
                        {col} {detection.detected.quantity === col && '(détecté)'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Colonne Produit <span className="text-slate-400">(optionnel)</span>
                  </label>
                  <select
                    value={productColumn}
                    onChange={(e) => setProductColumn(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Aucun (agrégé)</option>
                    {detection.columns.map((col) => (
                      <option key={col} value={col}>
                        {col} {detection.detected.product === col && '(détecté)'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mt-6 p-4 bg-slate-50 rounded-lg">
                <p className="text-sm font-medium text-slate-700 mb-2">Aperçu des données</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="bg-slate-200">
                        {detection.columns.slice(0, 5).map((col) => (
                          <th key={col} className="px-2 py-1 text-left font-medium text-slate-600">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {detection.sample_data.slice(0, 3).map((row, i) => (
                        <tr key={i} className="border-b border-slate-200">
                          {detection.columns.slice(0, 5).map((col) => (
                            <td key={col} className="px-2 py-1 text-slate-600">
                              {String(row[col]).substring(0, 20)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}

              <div className="mt-6 flex gap-3">
                <button
                  onClick={resetUpload}
                  className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleLoadData}
                  disabled={loading || !dateColumn || !quantityColumn}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Chargement...
                    </>
                  ) : (
                    'Charger les données'
                  )}
                </button>
              </div>
            </>
          )}

          {step === 'success' && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">
                Données importées avec succès !
              </h3>
              <p className="text-slate-600">
                Vous pouvez maintenant générer des prédictions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
