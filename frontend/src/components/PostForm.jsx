import { useState, useEffect } from 'react'
import axios from 'axios'
import { X, Send } from 'lucide-react'

const PostForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'geral',
    is_anonymous: false
  })
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/forum/categories')
      setCategories(response.data.categories)
    } catch (error) {
      console.error('Erro ao carregar categorias:', error)
    }
  }

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

    if (!formData.title.trim() || !formData.content.trim()) {
      setError('Título e conteúdo são obrigatórios')
      return
    }

    setLoading(true)

    try {
      await axios.post('/api/forum/posts', formData)
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar post')
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
          Título *
        </label>
        <input
          type="text"
          name="title"
          required
          value={formData.title}
          onChange={handleChange}
          className="input-field"
          placeholder="Título do post"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Categoria
        </label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="input-field"
        >
          {categories.map(cat => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Conteúdo *
        </label>
        <textarea
          name="content"
          required
          value={formData.content}
          onChange={handleChange}
          rows={6}
          className="input-field"
          placeholder="Compartilhe sua experiência, dúvida ou pensamento..."
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          name="is_anonymous"
          checked={formData.is_anonymous}
          onChange={handleChange}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
        />
        <label className="ml-2 block text-sm text-gray-700">
          Publicar como anônimo
        </label>
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50"
        >
          {loading ? 'Publicando...' : (
            <>
              <Send className="mr-2" size={18} />
              Publicar
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

export default PostForm

