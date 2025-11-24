import { useState } from 'react'
import axios from 'axios'
import { Star, X, Send } from 'lucide-react'

const ReviewForm = ({ psychologist, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    rating: 0,
    comment: ''
  })
  const [hoveredRating, setHoveredRating] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleRatingClick = (rating) => {
    setFormData(prev => ({ ...prev, rating }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.rating === 0) {
      setError('Por favor, selecione uma avaliação')
      return
    }

    setLoading(true)

    try {
      const reviewData = {
        psychologist_id: psychologist.id,
        rating: formData.rating,
        comment: formData.comment || null
      }

      await axios.post('/api/reviews/', reviewData)
      onSuccess()
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Erro ao criar avaliação'
      // Mensagem mais amigável para o erro de consulta não concluída
      if (errorMessage.includes('consultas concluídas') || err.response?.status === 403) {
        setError('Você só pode avaliar psicólogos com os quais já teve consultas concluídas. Agende e complete uma consulta primeiro.')
      } else {
        setError(errorMessage)
      }
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

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Avaliação *
        </label>
        <div className="flex items-center gap-2">
          {[1, 2, 3, 4, 5].map((rating) => (
            <button
              key={rating}
              type="button"
              onClick={() => handleRatingClick(rating)}
              onMouseEnter={() => setHoveredRating(rating)}
              onMouseLeave={() => setHoveredRating(0)}
              className="focus:outline-none"
            >
              <Star
                className={`${
                  rating <= (hoveredRating || formData.rating)
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-gray-300'
                } transition-colors`}
                size={32}
              />
            </button>
          ))}
          {formData.rating > 0 && (
            <span className="ml-2 text-sm text-gray-600">
              {formData.rating} {formData.rating === 1 ? 'estrela' : 'estrelas'}
            </span>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Comentário (opcional)
        </label>
        <textarea
          name="comment"
          value={formData.comment}
          onChange={handleChange}
          rows={4}
          className="input-field"
          placeholder="Compartilhe sua experiência com este psicólogo..."
        />
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading || formData.rating === 0}
          className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Enviando...' : (
            <>
              <Send className="mr-2" size={18} />
              Enviar Avaliação
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

export default ReviewForm

