import { useState, useCallback } from 'react'
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL

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
    if (droppedFile) processFile(droppedFile)
  }, [])

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) processFile(selectedFile)
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
          {loading && step === 'upload' && (
            <div className="text-center py-8">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
              <p>Analyse en cours...</p>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
