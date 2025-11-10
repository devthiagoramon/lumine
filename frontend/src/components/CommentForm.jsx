import { useState } from 'react'
import axios from 'axios'
import { Send } from 'lucide-react'

const CommentForm = ({ postId, onSuccess }) => {
  const [formData, setFormData] = useState({
    content: '',
    is_anonymous: false
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!formData.content.trim()) {
      setError('Comentário não pode estar vazio')
      return
    }

    setLoading(true)

    try {
      await axios.post(`/api/forum/posts/${postId}/comments`, formData)
      setFormData({ content: '', is_anonymous: false })
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar comentário')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <div>
        <textarea
          name="content"
          required
          value={formData.content}
          onChange={handleChange}
          rows={3}
          className="input-field"
          placeholder="Escreva seu comentário..."
        />
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center">
          <input
            type="checkbox"
            name="is_anonymous"
            checked={formData.is_anonymous}
            onChange={handleChange}
            className="mr-2"
          />
          <span className="text-sm text-gray-700">Comentar como anônimo</span>
        </label>
        <button
          type="submit"
          disabled={loading || !formData.content.trim()}
          className="btn-primary text-sm px-4 py-2 flex items-center disabled:opacity-50"
        >
          {loading ? 'Enviando...' : (
            <>
              <Send className="mr-2" size={16} />
              Comentar
            </>
          )}
        </button>
      </div>
    </form>
  )
}

export default CommentForm

