import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Calendar, Heart, Plus, Edit, Trash2, TrendingUp, BarChart3 } from 'lucide-react'
import EmotionEntryForm from '../components/EmotionEntryForm'

const EmotionDiary = () => {
  const { user, loading: authLoading } = useAuth()
  const { success, error: showError } = useToast()
  const navigate = useNavigate()
  const [entries, setEntries] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingEntry, setEditingEntry] = useState(null)
  const [emotions, setEmotions] = useState([])
  const [selectedEmotion, setSelectedEmotion] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login')
    } else if (user) {
      fetchEmotions()
      fetchEntries()
      fetchStats()
    }
  }, [user, authLoading, navigate, selectedEmotion, startDate, endDate])

  const fetchEmotions = async () => {
    try {
      const response = await axios.get('/api/emotion-diary/emotions/list')
      setEmotions(response.data.emotions)
    } catch (error) {
      console.error('Erro ao carregar emoções:', error)
    }
  }

  const fetchEntries = async () => {
    setLoading(true)
    try {
      const params = {}
      if (selectedEmotion) params.emotion = selectedEmotion
      if (startDate) params.start_date = new Date(startDate).toISOString()
      if (endDate) params.end_date = new Date(endDate).toISOString()

      const response = await axios.get('/api/emotion-diary/', { params })
      setEntries(response.data)
    } catch (error) {
      console.error('Erro ao carregar entradas:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const params = {}
      if (startDate) params.start_date = new Date(startDate).toISOString()
      if (endDate) params.end_date = new Date(endDate).toISOString()

      const response = await axios.get('/api/emotion-diary/stats', { params })
      setStats(response.data)
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    }
  }

  const handleEntryCreated = () => {
    setShowForm(false)
    setEditingEntry(null)
    fetchEntries()
    fetchStats()
  }

  const handleEdit = (entry) => {
    setEditingEntry(entry)
    setShowForm(true)
  }

  const handleDelete = async (entryId) => {
    if (!window.confirm('Tem certeza que deseja excluir esta entrada?')) {
      return
    }

    try {
      await axios.delete(`/api/emotion-diary/${entryId}`)
      fetchEntries()
      fetchStats()
      success('Entrada excluída com sucesso')
    } catch (error) {
      console.error('Erro ao excluir entrada:', error)
      showError('Erro ao excluir entrada')
    }
  }

  const getEmotionColor = (emotion) => {
    const colors = {
      'feliz': 'bg-yellow-100 text-yellow-800',
      'triste': 'bg-blue-100 text-blue-800',
      'ansioso': 'bg-orange-100 text-orange-800',
      'irritado': 'bg-red-100 text-red-800',
      'calmo': 'bg-green-100 text-green-800',
      'estressado': 'bg-purple-100 text-purple-800',
      'motivado': 'bg-pink-100 text-pink-800',
      'cansado': 'bg-gray-100 text-gray-800',
      'gratidão': 'bg-amber-100 text-amber-800',
      'medo': 'bg-indigo-100 text-indigo-800',
      'raiva': 'bg-red-200 text-red-900',
      'esperança': 'bg-cyan-100 text-cyan-800',
      'confuso': 'bg-slate-100 text-slate-800',
      'orgulhoso': 'bg-emerald-100 text-emerald-800',
      'culpado': 'bg-rose-100 text-rose-800'
    }
    return colors[emotion] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Diário de Emoções
            </h1>
            <p className="text-gray-600">
              Registre suas emoções e acompanhe seu bem-estar emocional
            </p>
          </div>
          <button
            onClick={() => {
              setShowForm(true)
              setEditingEntry(null)
            }}
            className="btn-primary flex items-center"
          >
            <Plus className="mr-2" size={18} />
            Nova Entrada
          </button>
        </div>

        {/* Form */}
        {showForm && (
          <div className="card p-6 mb-6">
            <EmotionEntryForm
              entry={editingEntry}
              onSuccess={handleEntryCreated}
              onCancel={() => {
                setShowForm(false)
                setEditingEntry(null)
              }}
            />
          </div>
        )}

        {/* Stats */}
        {stats && (
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total de Entradas</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_entries}</p>
                </div>
                <Calendar className="text-primary-600" size={32} />
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Intensidade Média</p>
                  <p className="text-3xl font-bold text-primary-600">
                    {stats.average_intensity.toFixed(1)}
                  </p>
                </div>
                <TrendingUp className="text-primary-600" size={32} />
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Emoções Registradas</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.emotion_stats.length}</p>
                </div>
                <BarChart3 className="text-primary-600" size={32} />
              </div>
            </div>
          </div>
        )}

        {/* Emotion Stats */}
        {stats && stats.emotion_stats.length > 0 && (
          <div className="card p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Estatísticas por Emoção</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {stats.emotion_stats.map(stat => (
                <div key={stat.emotion} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEmotionColor(stat.emotion)}`}>
                      {emotions.find(e => e.value === stat.emotion)?.label || stat.emotion}
                    </span>
                    <span className="text-sm text-gray-600">{stat.count}x</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${(stat.average_intensity / 10) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">
                      {stat.average_intensity.toFixed(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="card p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Filtros</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Emoção
              </label>
              <select
                value={selectedEmotion}
                onChange={(e) => setSelectedEmotion(e.target.value)}
                className="input-field"
              >
                <option value="">Todas as emoções</option>
                {emotions.map(emotion => (
                  <option key={emotion.value} value={emotion.value}>
                    {emotion.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Inicial
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Final
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* Entries List */}
        {entries.length === 0 ? (
          <div className="card p-8 text-center">
            <Heart className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600 text-lg mb-4">
              Nenhuma entrada registrada ainda
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary inline-flex items-center"
            >
              <Plus className="mr-2" size={18} />
              Criar Primeira Entrada
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {entries.map(entry => (
              <div key={entry.id} className="card p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getEmotionColor(entry.emotion)}`}>
                        {emotions.find(e => e.value === entry.emotion)?.label || entry.emotion}
                      </span>
                      <div className="flex items-center gap-1">
                        {[...Array(10)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-3 h-3 rounded-full ${
                              i < entry.intensity
                                ? 'bg-primary-600'
                                : 'bg-gray-200'
                            }`}
                          ></div>
                        ))}
                        <span className="ml-2 text-sm text-gray-600">
                          {entry.intensity}/10
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-600 mb-2">
                      <Calendar className="inline mr-1" size={16} />
                      {formatDate(entry.date)}
                    </p>
                    {entry.notes && (
                      <p className="text-gray-700 whitespace-pre-line mb-2">
                        {entry.notes}
                      </p>
                    )}
                    {entry.tags && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {entry.tags.split(',').map((tag, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                          >
                            {tag.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(entry)}
                      className="text-primary-600 hover:text-primary-700"
                      title="Editar"
                    >
                      <Edit size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(entry.id)}
                      className="text-red-600 hover:text-red-700"
                      title="Excluir"
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
    </div>
  )
}

export default EmotionDiary

