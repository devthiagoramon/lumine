import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Edit, Trash2, Eye, MessageSquare, User, Search, Filter, AlertCircle, Loader } from 'lucide-react'

const ForumManagement = () => {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPostForm, setShowPostForm] = useState(false)
  const [editingPost, setEditingPost] = useState(null)
  const [category, setCategory] = useState('')
  const [search, setSearch] = useState('')
  const [categories, setCategories] = useState([])

  useEffect(() => {
    fetchCategories()
    fetchPosts()
  }, [category, search])

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/forum/categories')
      setCategories(response.data.categories)
    } catch (error) {
      console.error('Erro ao carregar categorias:', error)
    }
  }

  const fetchPosts = async () => {
    setLoading(true)
    try {
      const params = {}
      if (category) params.category = category
      if (search) params.search = search

      const response = await axios.get('/api/forum/posts', { params })
      setPosts(response.data)
    } catch (error) {
      console.error('Erro ao carregar posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePostCreated = () => {
    setShowPostForm(false)
    fetchPosts()
  }

  const handleEdit = (post) => {
    setEditingPost(post)
    setShowPostForm(true)
  }

  const handleDelete = async (postId) => {
    if (!window.confirm('Tem certeza que deseja excluir este post?')) {
      return
    }

    try {
      await axios.delete(`/api/admin/forum/posts/${postId}`)
      fetchPosts()
    } catch (error) {
      console.error('Erro ao excluir post:', error)
      alert('Erro ao excluir post')
    }
  }

  const handleUpdate = async (postId, data) => {
    try {
      await axios.put(`/api/admin/forum/posts/${postId}`, data)
      setEditingPost(null)
      setShowPostForm(false)
      fetchPosts()
    } catch (error) {
      console.error('Erro ao atualizar post:', error)
      alert('Erro ao atualizar post')
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gerenciamento de Fóruns</h2>
          <p className="text-gray-600 text-sm mt-1">
            Crie, edite ou remova posts do fórum
          </p>
        </div>
        <button
          onClick={() => {
            setEditingPost(null)
            setShowPostForm(!showPostForm)
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={18} />
          {showPostForm ? 'Cancelar' : 'Novo Post'}
        </button>
      </div>

      {/* Post Form */}
      {showPostForm && (
        <div className="mb-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
          {editingPost ? (
            <EditPostForm
              post={editingPost}
              onSuccess={handlePostCreated}
              onCancel={() => {
                setShowPostForm(false)
                setEditingPost(null)
              }}
              onUpdate={handleUpdate}
            />
          ) : (
            <AdminPostForm
              onSuccess={handlePostCreated}
              onCancel={() => setShowPostForm(false)}
            />
          )}
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Buscar posts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="input-field pl-10 pr-8"
          >
            <option value="">Todas as categorias</option>
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12">
          <MessageSquare className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600 text-lg">Nenhum post encontrado</p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map(post => (
            <div
              key={post.id}
              className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold text-gray-900">{post.title}</h3>
                    <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                      {categories.find(c => c.value === post.category)?.label || post.category}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    {post.is_anonymous ? (
                      <span className="flex items-center gap-1">
                        <User size={14} />
                        Anônimo
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <User size={14} />
                        {post.user?.full_name || 'Usuário'}
                      </span>
                    )}
                    <span>{formatDate(post.created_at)}</span>
                    <span className="flex items-center gap-1">
                      <Eye size={14} />
                      {post.views} visualizações
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageSquare size={14} />
                      {post.comments_count || 0} comentários
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-line mb-4">{post.content}</p>
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => handleEdit(post)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Editar post"
                  >
                    <Edit size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(post.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Excluir post"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Componente para criar post como admin
const AdminPostForm = ({ onSuccess, onCancel }) => {
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
      await axios.post('/api/admin/forum/posts', formData)
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Título *</label>
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Conteúdo *</label>
        <textarea
          name="content"
          required
          value={formData.content}
          onChange={handleChange}
          rows={6}
          className="input-field"
          placeholder="Conteúdo do post..."
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
        <label className="ml-2 block text-sm text-gray-700">Publicar como anônimo</label>
      </div>
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 disabled:opacity-50"
        >
          {loading ? 'Publicando...' : 'Publicar'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}

// Componente para editar post
const EditPostForm = ({ post, onSuccess, onCancel, onUpdate }) => {
  const [formData, setFormData] = useState({
    title: post.title || '',
    content: post.content || '',
    category: post.category || 'geral'
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
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
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
      await onUpdate(post.id, formData)
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao atualizar post')
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Título *</label>
        <input
          type="text"
          name="title"
          required
          value={formData.title}
          onChange={handleChange}
          className="input-field"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
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
        <label className="block text-sm font-medium text-gray-700 mb-2">Conteúdo *</label>
        <textarea
          name="content"
          required
          value={formData.content}
          onChange={handleChange}
          rows={6}
          className="input-field"
        />
      </div>
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 disabled:opacity-50"
        >
          {loading ? 'Atualizando...' : 'Atualizar'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default ForumManagement

