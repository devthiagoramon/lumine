import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import axios from 'axios'
import { MapPin, Star, Monitor, Building2, Calendar, CheckCircle, Heart, MessageSquare, Plus, Clock } from 'lucide-react'
import AppointmentForm from '../components/AppointmentForm'
import ReviewForm from '../components/ReviewForm'

const PsychologistProfile = () => {
  const { id } = useParams()
  const { user: currentUser } = useAuth()
  const { success, error: showError } = useToast()
  const navigate = useNavigate()
  const [psychologist, setPsychologist] = useState(null)
  const [reviews, setReviews] = useState([])
  const [isFavorite, setIsFavorite] = useState(false)
  const [showAppointmentForm, setShowAppointmentForm] = useState(false)
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [reviewsLoading, setReviewsLoading] = useState(false)
  const [discountInfo, setDiscountInfo] = useState(null)

  const handleAgendarConsulta = () => {
    if (!currentUser) {
      // Redirecionar para login se não estiver logado
      if (window.confirm('Você precisa estar logado para agendar uma consulta. Deseja fazer login?')) {
        navigate('/login')
      }
      return
    }
    
    if (currentUser.eh_psicologo) {
      showError('Psicólogos não podem agendar consultas com outros psicólogos.')
      return
    }
    
    setShowAppointmentForm(!showAppointmentForm)
  }

  useEffect(() => {
    fetchPsychologist()
    if (currentUser) {
      checkFavorite()
      checkDiscount()
    }
  }, [id, currentUser])

  const checkDiscount = async () => {
    if (!currentUser || currentUser.eh_psicologo) return
    try {
      const response = await axios.get(`/api/appointments/verificar-primeira-consulta/${id}`)
      setDiscountInfo(response.data)
    } catch (error) {
      console.error('Erro ao verificar desconto:', error)
    }
  }

  const fetchPsychologist = async () => {
    try {
      const response = await axios.get(`/api/psychologists/${id}`)
      console.log('Dados do psicólogo recebidos:', response.data)
      setPsychologist(response.data)
      fetchReviews()
    } catch (error) {
      console.error('Erro ao carregar perfil:', error)
      console.error('Resposta completa:', error.response)
      showError('Erro ao carregar perfil do psicólogo')
    } finally {
      setLoading(false)
    }
  }

  const fetchReviews = async () => {
    setReviewsLoading(true)
    try {
      const response = await axios.get(`/api/reviews/psychologist/${id}`)
      setReviews(response.data)
    } catch (error) {
      console.error('Erro ao carregar avaliações:', error)
    } finally {
      setReviewsLoading(false)
    }
  }

  const checkFavorite = async () => {
    try {
      const response = await axios.get(`/api/favorites/check/${id}`)
      setIsFavorite(response.data.is_favorite)
    } catch (error) {
      console.error('Erro ao verificar favorito:', error)
    }
  }

  const handleToggleFavorite = async () => {
    if (!currentUser) {
      showError('Você precisa estar logado para adicionar aos favoritos')
      return
    }

    try {
      if (isFavorite) {
        await axios.delete(`/api/favorites/${id}`)
        setIsFavorite(false)
        success('Removido dos favoritos')
      } else {
        await axios.post(`/api/favorites/${id}`)
        setIsFavorite(true)
        success('Adicionado aos favoritos')
      }
    } catch (error) {
      console.error('Erro ao atualizar favorito:', error)
      showError('Erro ao atualizar favorito')
    }
  }

  const handleAppointmentSuccess = () => {
    setShowAppointmentForm(false)
    success('Agendamento criado com sucesso! Redirecionando para seu dashboard...')
    setTimeout(() => {
      navigate('/dashboard/cliente', { state: { message: 'Agendamento criado com sucesso!' } })
    }, 1500)
  }

  const handleReviewSuccess = () => {
    setShowReviewForm(false)
    fetchPsychologist()
    fetchReviews()
    success('Avaliação enviada com sucesso!')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg mb-6"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!psychologist) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="card p-8 text-center">
            <p className="text-gray-600">Psicólogo não encontrado</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="card p-8 mb-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="w-32 h-32 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center text-white text-5xl font-bold">
              {psychologist.user.nome_completo.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">
                  {psychologist.user.nome_completo}
                </h1>
                {psychologist.is_verified && (
                  <CheckCircle className="text-primary-600" size={24} />
                )}
              </div>
              <p className="text-gray-600 mb-2">CRP: {psychologist.crp}</p>
              {psychologist.rating > 0 && (
                <div className="flex items-center gap-2">
                  <Star className="text-yellow-400 fill-yellow-400" size={20} />
                  <span className="font-semibold text-gray-900">
                    {psychologist.rating.toFixed(1)}
                  </span>
                  <span className="text-gray-600">
                    ({psychologist.total_reviews} avaliações)
                  </span>
                </div>
              )}
              {psychologist.consultation_price && (
                <div className="mt-3">
                  {discountInfo && discountInfo.is_first_appointment ? (
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xl line-through text-gray-400">
                          R$ {discountInfo.original_price.toFixed(2)}
                        </span>
                        <span className="text-2xl font-bold text-primary-600">
                          R$ {discountInfo.discounted_price.toFixed(2)}
                        </span>
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-semibold">
                          -30%
                        </span>
                      </div>
                      <p className="text-sm text-green-600 font-medium">
                        🎉 Desconto especial para primeira consulta!
                      </p>
                      <span className="text-gray-600 text-sm">por consulta</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-primary-600">
                        R$ {psychologist.consultation_price.toFixed(2)}
                      </span>
                      <span className="text-gray-600">por consulta</span>
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="flex flex-col gap-3 w-full md:w-auto">
              {/* Botão de Agendar Consulta - Sempre visível */}
              <button
                onClick={handleAgendarConsulta}
                className="btn-primary flex items-center justify-center w-full md:w-auto px-6 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                <Calendar className="mr-2" size={20} />
                {showAppointmentForm ? 'Cancelar Agendamento' : 'Agendar Consulta'}
              </button>
              
              {/* Botão de Favoritos - Apenas para usuários logados que não são psicólogos */}
              {currentUser && !currentUser.eh_psicologo && (
                <button
                  onClick={handleToggleFavorite}
                  className={`btn-secondary flex items-center justify-center w-full md:w-auto ${
                    isFavorite ? 'bg-red-50 border-red-600 text-red-600' : ''
                  }`}
                >
                  <Heart
                    className={`mr-2 ${isFavorite ? 'fill-red-500' : ''}`}
                    size={18}
                  />
                  {isFavorite ? 'Remover dos Favoritos' : 'Adicionar aos Favoritos'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Appointment Form */}
        {showAppointmentForm && currentUser && !currentUser.is_psychologist && (
          <div className="card p-6 mb-6 border-2 border-primary-200">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="text-primary-600" size={24} />
              <h2 className="text-2xl font-bold text-gray-900">Agendar Consulta</h2>
            </div>
            <AppointmentForm
              psychologist={psychologist}
              onSuccess={handleAppointmentSuccess}
              onCancel={() => setShowAppointmentForm(false)}
            />
          </div>
        )}

        {/* Mensagem se não estiver logado */}
        {showAppointmentForm && !currentUser && (
          <div className="card p-6 mb-6 bg-yellow-50 border-2 border-yellow-200">
            <p className="text-gray-700 mb-4">
              Você precisa estar logado para agendar uma consulta. 
              <Link to="/login" className="text-primary-600 font-semibold ml-1 hover:underline">
                Clique aqui para fazer login
              </Link>
            </p>
            <button
              onClick={() => setShowAppointmentForm(false)}
              className="btn-secondary"
            >
              Cancelar
            </button>
          </div>
        )}

        {/* Bio */}
        {psychologist.bio && (
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Sobre</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {psychologist.bio}
            </p>
          </div>
        )}

        {/* Info Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Location */}
          {(psychologist.city || psychologist.address) && (
            <div className="card p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <MapPin className="mr-2 text-primary-600" size={24} />
                Localização
              </h3>
              {psychologist.address && (
                <p className="text-gray-700 mb-1">{psychologist.address}</p>
              )}
              {psychologist.city && psychologist.state && (
                <p className="text-gray-700">
                  {psychologist.city}, {psychologist.state}
                  {psychologist.zip_code && ` - ${psychologist.zip_code}`}
                </p>
              )}
            </div>
          )}

          {/* Consultation Types */}
          <div className="card p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Calendar className="mr-2 text-primary-600" size={24} />
              Tipos de Consulta
            </h3>
            <div className="space-y-2">
              {(psychologist.online_consultation === true || psychologist.online_consultation === 'true') && (
                <div className="flex items-center text-gray-700">
                  <Monitor className="mr-2 text-primary-600" size={20} />
                  <span>Consulta Online</span>
                </div>
              )}
              {(psychologist.in_person_consultation === true || psychologist.in_person_consultation === 'true') && (
                <div className="flex items-center text-gray-700">
                  <Building2 className="mr-2 text-primary-600" size={20} />
                  <span>Consulta Presencial</span>
                </div>
              )}
              {(!psychologist.online_consultation && !psychologist.in_person_consultation) && (
                <p className="text-gray-500 italic">Nenhum tipo de consulta configurado</p>
              )}
            </div>
            {psychologist.consultation_price && (
              <div className="mt-4">
                {discountInfo && discountInfo.is_first_appointment ? (
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-xl line-through text-gray-400">
                        R$ {discountInfo.original_price.toFixed(2)}
                      </p>
                      <p className="text-2xl font-bold text-primary-600">
                        R$ {discountInfo.discounted_price.toFixed(2)}
                      </p>
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm font-semibold">
                        -30%
                      </span>
                    </div>
                    <p className="text-sm text-green-600 font-medium mb-1">
                      🎉 Desconto especial para primeira consulta!
                    </p>
                    <p className="text-sm text-gray-600">por consulta</p>
                  </div>
                ) : (
                  <>
                    <p className="text-2xl font-bold text-primary-600">
                      R$ {psychologist.consultation_price.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600">por consulta</p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Specialties */}
        <div className="card p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Especialidades</h2>
          {psychologist.specialties && psychologist.specialties.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {psychologist.specialties.map(spec => (
                <div
                  key={spec.id}
                  className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg font-medium"
                >
                  {spec.name}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">Nenhuma especialidade cadastrada</p>
          )}
        </div>

        {/* Approaches */}
        <div className="card p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Abordagens Terapêuticas</h2>
          {psychologist.approaches && psychologist.approaches.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {psychologist.approaches.map(approach => (
                <div
                  key={approach.id}
                  className="px-4 py-2 bg-secondary-100 text-secondary-700 rounded-lg font-medium"
                >
                  {approach.name}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">Nenhuma abordagem terapêutica cadastrada</p>
          )}
        </div>

        {/* Experience */}
        {psychologist.experience_years > 0 && (
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Experiência</h2>
            <p className="text-gray-700">
              {psychologist.experience_years} {psychologist.experience_years === 1 ? 'ano' : 'anos'} de experiência
            </p>
          </div>
        )}

        {/* Reviews Section */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Avaliações</h2>
            {currentUser && !currentUser.is_psychologist && (
              <button
                onClick={() => setShowReviewForm(!showReviewForm)}
                className="btn-secondary flex items-center text-sm"
              >
                <MessageSquare className="mr-2" size={18} />
                {showReviewForm ? 'Cancelar' : 'Avaliar'}
              </button>
            )}
          </div>

          {/* Review Form */}
          {showReviewForm && currentUser && !currentUser.is_psychologist && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <ReviewForm
                psychologist={psychologist}
                onSuccess={handleReviewSuccess}
                onCancel={() => setShowReviewForm(false)}
              />
            </div>
          )}

          {/* Reviews List */}
          {reviewsLoading ? (
            <p className="text-gray-600 text-center py-4">Carregando avaliações...</p>
          ) : reviews.length === 0 ? (
            <p className="text-gray-600 text-center py-4">Nenhuma avaliação ainda</p>
          ) : (
            <div className="space-y-4">
              {reviews.map(review => (
                <div key={review.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">
                        {review.user.nome_completo}
                      </h3>
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`${
                              i < review.rating
                                ? 'text-yellow-400 fill-yellow-400'
                                : 'text-gray-300'
                            }`}
                            size={16}
                          />
                        ))}
                      </div>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(review.criado_em).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  {review.comment && (
                    <p className="text-gray-700 mt-2">{review.comment}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Contact Info */}
        {psychologist.user.telefone && (
          <div className="card p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Contato</h2>
            <div className="space-y-2">
              <p className="text-gray-700">
                <span className="font-medium">Email:</span> {psychologist.user.email}
              </p>
              {psychologist.user.telefone && (
                <p className="text-gray-700">
                  <span className="font-medium">Telefone:</span> {psychologist.user.telefone}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PsychologistProfile

