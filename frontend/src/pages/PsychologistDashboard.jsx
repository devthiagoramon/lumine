import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { Calendar, Star, Users, TrendingUp, Clock, CheckCircle, XCircle, MessageSquare } from 'lucide-react'

const PsychologistDashboard = () => {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [appointments, setAppointments] = useState([])
  const [reviews, setReviews] = useState([])
  const [stats, setStats] = useState({
    total_appointments: 0,
    pending_appointments: 0,
    confirmed_appointments: 0,
    completed_appointments: 0,
    total_reviews: 0,
    average_rating: 0
  })
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('appointments')

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login')
    } else if (user && !user.is_psychologist) {
      navigate('/dashboard')
    } else if (user) {
      fetchData()
    }
  }, [user, authLoading, navigate])

  const fetchData = async () => {
    try {
      const [appointmentsRes, reviewsRes] = await Promise.all([
        axios.get('/api/appointments/psychologist-appointments'),
        axios.get('/api/psychologists/me')
      ])
      
      setAppointments(appointmentsRes.data)
      
      if (reviewsRes.data) {
        const reviewsData = await axios.get(`/api/reviews/psychologist/${reviewsRes.data.id}`)
        setReviews(reviewsData.data)
        setStats({
          total_appointments: appointmentsRes.data.length,
          pending_appointments: appointmentsRes.data.filter(a => a.status === 'pending').length,
          confirmed_appointments: appointmentsRes.data.filter(a => a.status === 'confirmed').length,
          completed_appointments: appointmentsRes.data.filter(a => a.status === 'completed').length,
          total_reviews: reviewsRes.data.total_reviews || 0,
          average_rating: reviewsRes.data.rating || 0
        })
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateAppointment = async (appointmentId, status) => {
    try {
      await axios.put(`/api/appointments/${appointmentId}`, { status })
      fetchData()
    } catch (error) {
      console.error('Erro ao atualizar agendamento:', error)
      alert('Erro ao atualizar agendamento')
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

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Dashboard do Psicólogo
          </h1>
          <p className="text-gray-600">
            Gerencie seus agendamentos, avaliações e perfil profissional
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total de Agendamentos</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total_appointments}</p>
              </div>
              <Calendar className="text-primary-600" size={32} />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Pendentes</p>
                <p className="text-3xl font-bold text-yellow-600">{stats.pending_appointments}</p>
              </div>
              <Clock className="text-yellow-600" size={32} />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Confirmados</p>
                <p className="text-3xl font-bold text-green-600">{stats.confirmed_appointments}</p>
              </div>
              <CheckCircle className="text-green-600" size={32} />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Avaliação Média</p>
                <p className="text-3xl font-bold text-primary-600">
                  {stats.average_rating.toFixed(1)}
                </p>
                <p className="text-xs text-gray-500">({stats.total_reviews} avaliações)</p>
              </div>
              <Star className="text-yellow-400 fill-yellow-400" size={32} />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="card p-6 mb-6">
          <div className="flex space-x-4 border-b mb-6">
            <button
              onClick={() => setActiveTab('appointments')}
              className={`pb-4 px-4 font-medium transition-colors ${
                activeTab === 'appointments'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Agendamentos
            </button>
            <button
              onClick={() => setActiveTab('reviews')}
              className={`pb-4 px-4 font-medium transition-colors ${
                activeTab === 'reviews'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Avaliações
            </button>
          </div>

          {/* Appointments Tab */}
          {activeTab === 'appointments' && (
            <div className="space-y-4">
              {appointments.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  Nenhum agendamento encontrado
                </p>
              ) : (
                appointments.map(appointment => (
                  <div key={appointment.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {appointment.user.full_name}
                          </h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            appointment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            appointment.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                            appointment.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {appointment.status === 'pending' ? 'Pendente' :
                             appointment.status === 'confirmed' ? 'Confirmado' :
                             appointment.status === 'completed' ? 'Concluído' : 'Cancelado'}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-1">
                          <Calendar className="inline mr-1" size={16} />
                          {formatDate(appointment.appointment_date)}
                        </p>
                        <p className="text-gray-600 mb-1">
                          Tipo: {appointment.appointment_type === 'online' ? 'Online' : 'Presencial'}
                        </p>
                        {appointment.notes && (
                          <p className="text-gray-600 text-sm mt-2">
                            {appointment.notes}
                          </p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        {appointment.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleUpdateAppointment(appointment.id, 'confirmed')}
                              className="btn-primary text-sm px-4 py-2"
                            >
                              Confirmar
                            </button>
                            <button
                              onClick={() => handleUpdateAppointment(appointment.id, 'cancelled')}
                              className="btn-secondary text-sm px-4 py-2"
                            >
                              Cancelar
                            </button>
                          </>
                        )}
                        {appointment.status === 'confirmed' && (
                          <button
                            onClick={() => handleUpdateAppointment(appointment.id, 'completed')}
                            className="btn-primary text-sm px-4 py-2"
                          >
                            Marcar como Concluído
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Reviews Tab */}
          {activeTab === 'reviews' && (
            <div className="space-y-4">
              {reviews.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  Nenhuma avaliação ainda
                </p>
              ) : (
                reviews.map(review => (
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
                ))
              )}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Ações Rápidas</h2>
          <div className="flex flex-wrap gap-4">
            <Link to="/dashboard" className="btn-secondary">
              Editar Perfil
            </Link>
            <Link to="/buscar" className="btn-secondary">
              Ver Psicólogos
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PsychologistDashboard

