import { useState, useEffect } from 'react'
import axios from 'axios'
import { Save, X, Calendar, Heart } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const EmotionEntryForm = ({ entry, onSuccess, onCancel }) => {
  const { success } = useToast()
  const [formData, setFormData] = useState({
    date: new Date().toISOString().slice(0, 16),
    emotion: 'feliz',
    intensity: 5,
    notes: '',
    tags: ''
  })
  const [emotions, setEmotions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchEmotions()
    if (entry) {
      setFormData({
        date: new Date(entry.date).toISOString().slice(0, 16),
        emotion: entry.emotion,
        intensity: entry.intensity,
        notes: entry.notes || '',
        tags: entry.tags || ''
      })
    }
  }, [entry])

  const fetchEmotions = async () => {
    try {
      const response = await axios.get('/api/emotion-diary/emotions/list')
      setEmotions(response.data.emotions)
    } catch (error) {
      console.error('Erro ao carregar emoções:', error)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'intensity' ? parseInt(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.intensity < 1 || formData.intensity > 10) {
      setError('Intensidade deve estar entre 1 e 10')
      return
    }

    setLoading(true)

    try {
      const entryData = {
        date: new Date(formData.date).toISOString(),
        emotion: formData.emotion,
        intensity: formData.intensity,
        notes: formData.notes || null,
        tags: formData.tags || null
      }

      if (entry) {
        await axios.put(`/api/emotion-diary/${entry.id}`, entryData)
        success('Entrada atualizada com sucesso!')
      } else {
        await axios.post('/api/emotion-diary/', entryData)
        success('Entrada salva com sucesso!')
      }
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar entrada')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data e Hora *
          </label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="datetime-local"
              name="date"
              required
              value={formData.date}
              onChange={handleChange}
              className="input-field pl-10"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Emoção *
          </label>
          <div className="relative">
            <Heart className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <select
              name="emotion"
              required
              value={formData.emotion}
              onChange={handleChange}
              className="input-field pl-10"
            >
              {emotions.map(emotion => (
                <option key={emotion.value} value={emotion.value}>
                  {emotion.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Intensidade: {formData.intensity}/10 *
        </label>
        <input
          type="range"
          name="intensity"
          min="1"
          max="10"
          value={formData.intensity}
          onChange={handleChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>1</span>
          <span>5</span>
          <span>10</span>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Notas (opcional)
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={4}
          className="input-field"
          placeholder="Descreva o que você está sentindo, o que aconteceu, ou qualquer observação..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tags (opcional, separadas por vírgula)
        </label>
        <input
          type="text"
          name="tags"
          value={formData.tags}
          onChange={handleChange}
          className="input-field"
          placeholder="Ex: trabalho, família, exercício"
        />
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50"
        >
          {loading ? 'Salvando...' : (
            <>
              <Save className="mr-2" size={18} />
              {entry ? 'Atualizar' : 'Salvar'}
            </>
          )}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary flex items-center"
          >
            <X className="mr-2" size={18} />
            Cancelar
          </button>
        )}
      </div>
    </form>
  )
}

export default EmotionEntryForm

