import { useState, useEffect } from 'react'
import axios from 'axios'
import { CheckCircle, XCircle, User, Mail, Phone, MapPin, Briefcase, Star, AlertCircle, Loader } from 'lucide-react'

const PsychologistManagement = () => {
  const [psychologists, setPsychologists] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending') // 'pending', 'verified', 'all'
  const [error, setError] = useState('')

  useEffect(() => {
    fetchPsychologists()
  }, [filter])

  const fetchPsychologists = async () => {
    setLoading(true)
    setError('')
    try {
      let response
      if (filter === 'pending') {
        response = await axios.get('/api/admin/psychologists/pending')
        setPsychologists(response.data)
      } else {
        // Para verified e all, usar a rota normal de listagem
        response = await axios.get('/api/psychologists/')
        let data = response.data
        if (filter === 'verified') {
          data = data.filter(p => p.is_verified)
        }
        setPsychologists(data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar psicólogos')
      console.error('Erro ao carregar psicólogos:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (id) => {
    try {
      await axios.put(`/api/admin/psychologists/${id}/verify`)
      fetchPsychologists()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao validar psicólogo')
      console.error('Erro ao validar psicólogo:', err)
    }
  }

  const handleUnverify = async (id) => {
    if (!window.confirm('Tem certeza que deseja remover a validação deste psicólogo?')) {
      return
    }
    try {
      await axios.put(`/api/admin/psychologists/${id}/unverify`)
      fetchPsychologists()
    } catch (err) {
      alert(err.response?.data?.detail || 'Erro ao remover validação')
      console.error('Erro ao remover validação:', err)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'pending'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Pendentes ({filter === 'pending' ? psychologists.length : '...'})
        </button>
        <button
          onClick={() => setFilter('verified')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'verified'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Validados
        </button>
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todos
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-600">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : psychologists.length === 0 ? (
        <div className="text-center py-12">
          <User className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600 text-lg">
            {filter === 'pending' 
              ? 'Nenhum psicólogo pendente de validação'
              : 'Nenhum psicólogo encontrado'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {psychologists.map(psychologist => (
            <div
              key={psychologist.id}
              className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center text-white text-xl font-bold">
                      {psychologist.user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {psychologist.user.full_name}
                      </h3>
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Mail size={14} />
                          {psychologist.user.email}
                        </span>
                        {psychologist.user.phone && (
                          <span className="flex items-center gap-1">
                            <Phone size={14} />
                            {psychologist.user.phone}
                          </span>
                        )}
                      </div>
                    </div>
                    {psychologist.is_verified ? (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium flex items-center gap-1">
                        <CheckCircle size={14} />
                        Validado
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium flex items-center gap-1">
                        <AlertCircle size={14} />
                        Pendente
                      </span>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">CRP</p>
                      <p className="font-medium text-gray-900">{psychologist.crp}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                        <Briefcase size={14} />
                        Experiência
                      </p>
                      <p className="font-medium text-gray-900">
                        {psychologist.experience_years} {psychologist.experience_years === 1 ? 'ano' : 'anos'}
                      </p>
                    </div>
                    {psychologist.city && psychologist.state && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                          <MapPin size={14} />
                          Localização
                        </p>
                        <p className="font-medium text-gray-900">
                          {psychologist.city}, {psychologist.state}
                        </p>
                      </div>
                    )}
                    {psychologist.rating > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                          <Star size={14} className="text-yellow-400 fill-yellow-400" />
                          Avaliação
                        </p>
                        <p className="font-medium text-gray-900">
                          {psychologist.rating.toFixed(1)} ({psychologist.total_reviews} avaliações)
                        </p>
                      </div>
                    )}
                  </div>

                  {psychologist.bio && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-1">Sobre</p>
                      <p className="text-gray-700 whitespace-pre-line">{psychologist.bio}</p>
                    </div>
                  )}

                  {psychologist.specialties.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Especialidades</p>
                      <div className="flex flex-wrap gap-2">
                        {psychologist.specialties.map(spec => (
                          <span
                            key={spec.id}
                            className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs"
                          >
                            {spec.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Cadastrado em: {formatDate(psychologist.created_at)}
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  {!psychologist.is_verified ? (
                    <button
                      onClick={() => handleVerify(psychologist.id)}
                      className="btn-primary flex items-center justify-center gap-2 whitespace-nowrap"
                    >
                      <CheckCircle size={18} />
                      Validar
                    </button>
                  ) : (
                    <button
                      onClick={() => handleUnverify(psychologist.id)}
                      className="btn-secondary flex items-center justify-center gap-2 whitespace-nowrap"
                    >
                      <XCircle size={18} />
                      Remover Validação
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PsychologistManagement

