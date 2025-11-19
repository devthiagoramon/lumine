import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import axios from 'axios'
import { MessageSquare, Eye, Heart, Plus, Search, Filter, User, Edit, Trash2 } from 'lucide-react'
import PostForm from '../components/PostForm'
import CommentForm from '../components/CommentForm'

const Forum = () => {
  const { user } = useAuth()
  const { success, error: showError } = useToast()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPostForm, setShowPostForm] = useState(false)
  const [selectedPost, setSelectedPost] = useState(null)
  const [comments, setComments] = useState({})
  const [showComments, setShowComments] = useState({})
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

  const fetchComments = async (postId) => {
    try {
      const response = await axios.get(`/api/forum/posts/${postId}/comments`)
      setComments(prev => ({ ...prev, [postId]: response.data }))
    } catch (error) {
      console.error('Erro ao carregar comentários:', error)
    }
  }

  const handlePostCreated = () => {
    setShowPostForm(false)
    fetchPosts()
  }

  const handleCommentCreated = (postId) => {
    fetchComments(postId)
    fetchPosts()
  }

  const handleToggleComments = (postId) => {
    setShowComments(prev => ({ ...prev, [postId]: !prev[postId] }))
    if (!comments[postId]) {
      fetchComments(postId)
    }
  }

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Tem certeza que deseja excluir este post?')) {
      return
    }

    try {
      await axios.delete(`/api/forum/posts/${postId}`)
      fetchPosts()
      success('Post excluído com sucesso')
    } catch (error) {
      console.error('Erro ao excluir post:', error)
      showError('Erro ao excluir post')
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Fórum de Discussão
            </h1>
            <p className="text-gray-600">
              Compartilhe experiências e receba apoio da comunidade
            </p>
          </div>
          {user && (
            <button
              onClick={() => setShowPostForm(!showPostForm)}
              className="btn-primary flex items-center"
            >
              <Plus className="mr-2" size={18} />
              Novo Post
            </button>
          )}
        </div>

        {/* Post Form */}
        {showPostForm && user && (
          <div className="card p-6 mb-6">
            <PostForm
              onSuccess={handlePostCreated}
              onCancel={() => setShowPostForm(false)}
            />
          </div>
        )}

        {/* Filters */}
        <div className="card p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
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
        </div>

        {/* Posts List */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : posts.length === 0 ? (
          <div className="card p-8 text-center">
            <MessageSquare className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600 text-lg mb-4">
              Nenhum post encontrado
            </p>
            {user && (
              <button
                onClick={() => setShowPostForm(true)}
                className="btn-primary inline-flex items-center"
              >
                <Plus className="mr-2" size={18} />
                Criar Primeiro Post
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map(post => (
              <div key={post.id} className="card p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold text-gray-900">
                        {post.title}
                      </h2>
                      <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                        {categories.find(c => c.value === post.category)?.label || post.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                      {post.is_anonymous ? (
                        <span className="flex items-center">
                          <User className="mr-1" size={16} />
                          Anônimo
                        </span>
                      ) : (
                        <span className="flex items-center">
                          <User className="mr-1" size={16} />
                          {post.user?.full_name || 'Usuário'}
                        </span>
                      )}
                      <span>{formatDate(post.created_at)}</span>
                      <span className="flex items-center">
                        <Eye className="mr-1" size={16} />
                        {post.views}
                      </span>
                      <span className="flex items-center">
                        <MessageSquare className="mr-1" size={16} />
                        {post.comments_count || 0}
                      </span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-line mb-4">
                      {post.content}
                    </p>
                  </div>
                  {user && post.user_id === user.id && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="text-red-600 hover:text-red-700"
                        title="Excluir post"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Comments Section */}
                <div className="border-t pt-4">
                  <button
                    onClick={() => handleToggleComments(post.id)}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-3"
                  >
                    {showComments[post.id] ? 'Ocultar' : 'Ver'} Comentários ({post.comments_count || 0})
                  </button>

                  {showComments[post.id] && (
                    <div className="space-y-4 mt-4">
                      {comments[post.id]?.map(comment => (
                        <div key={comment.id} className="bg-gray-50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            {comment.is_anonymous ? (
                              <span className="text-sm font-medium text-gray-700">
                                Anônimo
                              </span>
                            ) : (
                              <span className="text-sm font-medium text-gray-700">
                                {comment.user?.full_name || 'Usuário'}
                              </span>
                            )}
                            <span className="text-xs text-gray-500">
                              {formatDate(comment.created_at)}
                            </span>
                          </div>
                          <p className="text-gray-700">{comment.content}</p>
                        </div>
                      ))}

                      {user && (
                        <div className="mt-4">
                          <CommentForm
                            postId={post.id}
                            onSuccess={() => handleCommentCreated(post.id)}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Forum

