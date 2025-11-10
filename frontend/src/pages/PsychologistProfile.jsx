import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { MapPin, Star, Monitor, Building2, Calendar, CheckCircle, Heart, MessageSquare, Plus } from 'lucide-react'
import AppointmentForm from '../components/AppointmentForm'
import ReviewForm from '../components/ReviewForm'

const PsychologistProfile = () => {
  const { id } = useParams()
  const { user: currentUser } = useAuth()
  const [psychologist, setPsychologist] = useState(null)
  const [reviews, setReviews] = useState([])
  const [isFavorite, setIsFavorite] = useState(false)
  const [showAppointmentForm, setShowAppointmentForm] = useState(false)
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [reviewsLoading, setReviewsLoading] = useState(false)

  useEffect(() => {
    fetchPsychologist()
    if (currentUser) {
      checkFavorite()
    }
  }, [id, currentUser])

  const fetchPsychologist = async () => {
    try {
      const response = await axios.get(`/api/psychologists/${id}`)
      setPsychologist(response.data)
      fetchReviews()
    } catch (error) {
      console.error('Erro ao carregar perfil:', error)
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
      alert('Você precisa estar logado para adicionar aos favoritos')
      return
    }

    try {
      if (isFavorite) {
        await axios.delete(`/api/favorites/${id}`)
        setIsFavorite(false)
      } else {
        await axios.post(`/api/favorites/${id}`)
        setIsFavorite(true)
      }
    } catch (error) {
      console.error('Erro ao atualizar favorito:', error)
      alert('Erro ao atualizar favorito')
    }
  }

  const handleAppointmentSuccess = () => {
    setShowAppointmentForm(false)
    alert('Agendamento criado com sucesso!')
  }

  const handleReviewSuccess = () => {
    setShowReviewForm(false)
    fetchPsychologist()
    fetchReviews()
    alert('Avaliação enviada com sucesso!')
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
              {psychologist.user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">
                  {psychologist.user.full_name}
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
            </div>
            <div className="flex gap-3">
              {currentUser && !currentUser.is_psychologist && (
                <>
                  <button
                    onClick={() => setShowAppointmentForm(!showAppointmentForm)}
                    className="btn-primary flex items-center"
                  >
                    <Calendar className="mr-2" size={18} />
                    {showAppointmentForm ? 'Cancelar' : 'Agendar Consulta'}
                  </button>
                  <button
                    onClick={handleToggleFavorite}
                    className={`btn-secondary flex items-center ${
                      isFavorite ? 'bg-red-50 border-red-600 text-red-600' : ''
                    }`}
                  >
                    <Heart
                      className={`mr-2 ${isFavorite ? 'fill-red-500' : ''}`}
                      size={18}
                    />
                    {isFavorite ? 'Remover dos Favoritos' : 'Adicionar aos Favoritos'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Appointment Form */}
        {showAppointmentForm && currentUser && !currentUser.is_psychologist && (
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Agendar Consulta</h2>
            <AppointmentForm
              psychologist={psychologist}
              onSuccess={handleAppointmentSuccess}
              onCancel={() => setShowAppointmentForm(false)}
            />
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
              {psychologist.online_consultation && (
                <div className="flex items-center text-gray-700">
                  <Monitor className="mr-2 text-primary-600" size={20} />
                  <span>Consulta Online</span>
                </div>
              )}
              {psychologist.in_person_consultation && (
                <div className="flex items-center text-gray-700">
                  <Building2 className="mr-2 text-primary-600" size={20} />
                  <span>Consulta Presencial</span>
                </div>
              )}
            </div>
            {psychologist.consultation_price && (
              <div className="mt-4">
                <p className="text-2xl font-bold text-primary-600">
                  R$ {psychologist.consultation_price.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600">por consulta</p>
              </div>
            )}
          </div>
        </div>

        {/* Specialties */}
        {psychologist.specialties.length > 0 && (
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Especialidades</h2>
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
          </div>
        )}

        {/* Approaches */}
        {psychologist.approaches.length > 0 && (
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Abordagens Terapêuticas</h2>
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
          </div>
        )}

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
                        {review.user.full_name}
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
                      {new Date(review.created_at).toLocaleDateString('pt-BR')}
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
        {psychologist.user.phone && (
          <div className="card p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Contato</h2>
            <div className="space-y-2">
              <p className="text-gray-700">
                <span className="font-medium">Email:</span> {psychologist.user.email}
              </p>
              {psychologist.user.phone && (
                <p className="text-gray-700">
                  <span className="font-medium">Telefone:</span> {psychologist.user.phone}
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

