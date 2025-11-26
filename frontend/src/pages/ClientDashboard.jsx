import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { Calendar, Heart, Star, Clock, CheckCircle, XCircle, Plus, Search, CreditCard, DollarSign, AlertTriangle } from 'lucide-react'
import PaymentForm from '../components/PaymentForm'

const ClientDashboard = () => {
  const { user, loading: authLoading } = useAuth()
  const { success, error: showError } = useToast()
  const navigate = useNavigate()
  const [appointments, setAppointments] = useState([])
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('appointments')
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)
  const [cancelConfirm, setCancelConfirm] = useState(null)

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login')
    } else if (user && user.eh_psicologo) {
      navigate('/dashboard')
    } else if (user) {
      fetchData()
    }
  }, [user, authLoading, navigate])

  const fetchData = async () => {
    try {
      const [appointmentsRes, favoritesRes] = await Promise.all([
        axios.get('/api/appointments/meus-agendamentos'),
        axios.get('/api/favorites/')
      ])
      
      console.log('📅 DEBUG: Agendamentos recebidos:', appointmentsRes.data)
      console.log('📅 DEBUG: Número de agendamentos:', appointmentsRes.data?.length || 0)
      if (appointmentsRes.data && appointmentsRes.data.length > 0) {
        console.log('📅 DEBUG: Primeiro agendamento:', appointmentsRes.data[0])
        console.log('📅 DEBUG: appointment_date do primeiro:', appointmentsRes.data[0].appointment_date)
        console.log('📅 DEBUG: status do primeiro:', appointmentsRes.data[0].status)
        console.log('📅 DEBUG: payment_status do primeiro:', appointmentsRes.data[0].payment_status)
      }
      
      setAppointments(appointmentsRes.data || [])
      setFavorites(favoritesRes.data || [])
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
      console.error('Detalhes do erro:', error.response?.data)
      setAppointments([])
      setFavorites([])
      if (error.response?.status === 401) {
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveFavorite = async (psychologistId) => {
    try {
      await axios.delete(`/api/favorites/${psychologistId}`)
      fetchData()
    } catch (error) {
      console.error('Erro ao remover favorito:', error)
    }
  }

  const handleCancelAppointment = async (appointmentId) => {
    try {
      await axios.delete(`/api/appointments/${appointmentId}`)
      setCancelConfirm(null)
      fetchData()
      success('Agendamento cancelado com sucesso')
    } catch (error) {
      console.error('Erro ao cancelar agendamento:', error)
      showError('Erro ao cancelar agendamento')
    }
  }

  const handlePayAppointment = (appointment) => {
    setSelectedAppointment(appointment)
    setShowPaymentForm(true)
  }

  const handlePaymentSuccess = () => {
    setShowPaymentForm(false)
    setSelectedAppointment(null)
    fetchData()
  }

  const checkPaymentStatus = async (appointmentId) => {
    try {
      const response = await axios.get(`/api/payments/appointment/${appointmentId}`)
      return response.data
    } catch (error) {
      return null
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

  const upcomingAppointments = (appointments || []).filter(a => {
    if (!a || !a.appointment_date) {
      console.log('⚠️ DEBUG: Agendamento sem appointment_date:', a)
      return false
    }
    const appointmentDate = new Date(a.appointment_date)
    const now = new Date()
    const isFuture = appointmentDate > now
    // Incluir agendamentos confirmados e pendentes (pendentes ainda não pagos)
    const isValidStatus = a.status === 'confirmed' || a.status === 'pending'
    const result = isFuture && isValidStatus
    if (result) {
      console.log('✅ DEBUG: Agendamento futuro encontrado:', {
        id: a.id,
        date: a.appointment_date,
        status: a.status,
        appointmentDate: appointmentDate.toISOString(),
        now: now.toISOString()
      })
    }
    return result
  })
  const pastAppointments = (appointments || []).filter(a => {
    if (!a || !a.appointment_date) {
      return false
    }
    const appointmentDate = new Date(a.appointment_date)
    const now = new Date()
    return appointmentDate < now || a.status === 'completed'
  })
  
  console.log('📊 DEBUG: Total de agendamentos:', appointments?.length || 0)
  console.log('📊 DEBUG: Próximos agendamentos:', upcomingAppointments.length)
  console.log('📊 DEBUG: Agendamentos anteriores:', pastAppointments.length)

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Meu Dashboard
          </h1>
          <p className="text-gray-600">
            Gerencie seus agendamentos e psicólogos favoritos
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Próximos Agendamentos</p>
                <p className="text-3xl font-bold text-gray-900">{upcomingAppointments.length}</p>
              </div>
              <Calendar className="text-primary-600" size={32} />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Agendamentos Anteriores</p>
                <p className="text-3xl font-bold text-gray-900">{pastAppointments.length}</p>
              </div>
              <Clock className="text-gray-600" size={32} />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Favoritos</p>
                <p className="text-3xl font-bold text-gray-900">{favorites.length}</p>
              </div>
              <Heart className="text-red-500 fill-red-500" size={32} />
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
              onClick={() => setActiveTab('favorites')}
              className={`pb-4 px-4 font-medium transition-colors ${
                activeTab === 'favorites'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Favoritos
            </button>
          </div>

          {/* Appointments Tab */}
          {activeTab === 'appointments' && (
            <div className="space-y-6">
              {/* Upcoming Appointments */}
              {upcomingAppointments.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Próximos Agendamentos</h3>
                  <div className="space-y-4">
                    {upcomingAppointments.map(appointment => (
                      <div key={appointment.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Link
                                to={`/psicologo/${appointment.psychologist?.id || ''}`}
                                className="text-lg font-semibold text-primary-600 hover:text-primary-700"
                              >
                                {appointment.psychologist?.user?.nome_completo || 'Psicólogo não encontrado'}
                              </Link>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            appointment.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {appointment.status === 'pending' ? 'Aguardando Pagamento' : 'Confirmado'}
                          </span>
                          {appointment.payment_status === 'pending' && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                              Pagamento Pendente
                            </span>
                          )}
                          {appointment.payment_status === 'paid' && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                              Pago
                            </span>
                          )}
                        </div>
                        <p className="text-gray-600 mb-1">
                          <Calendar className="inline mr-1" size={16} />
                          {formatDate(appointment.appointment_date)}
                        </p>
                        <p className="text-gray-600 mb-1">
                          Tipo: {appointment.appointment_type === 'online' ? 'Online' : 'Presencial'}
                        </p>
                        {appointment.psychologist?.consultation_price && (
                          <p className="text-gray-700 font-semibold mb-1">
                            Valor: R$ {appointment.psychologist.consultation_price.toFixed(2)}
                          </p>
                        )}
                        {appointment.notes && (
                          <p className="text-gray-600 text-sm mt-2">
                            {appointment.notes}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-col gap-2">
                        {appointment.status === 'pending' && (
                          <button
                            onClick={() => handlePayAppointment(appointment)}
                            className="btn-primary text-sm px-4 py-2 flex items-center justify-center"
                          >
                            <CreditCard className="mr-2" size={16} />
                            Pagar Agora
                          </button>
                        )}
                        {appointment.status === 'confirmed' && appointment.payment_status === 'pending' && (
                          <button
                            onClick={() => handlePayAppointment(appointment)}
                            className="btn-primary text-sm px-4 py-2 flex items-center justify-center"
                          >
                            <CreditCard className="mr-2" size={16} />
                            Pagar Agora
                          </button>
                        )}
                        {appointment.status === 'rejected' && (
                          <div className="text-sm text-red-600 px-4 py-2">
                            <p className="font-medium">Agendamento recusado</p>
                            {appointment.rejection_reason && (
                              <p className="text-xs mt-1">{appointment.rejection_reason}</p>
                            )}
                          </div>
                        )}
                        {appointment.status !== 'rejected' && appointment.status !== 'completed' && (
                          <button
                            onClick={() => setCancelConfirm(appointment)}
                            className="btn-secondary text-sm px-4 py-2"
                          >
                            Cancelar
                          </button>
                        )}
                      </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Past Appointments */}
              {pastAppointments.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Agendamentos Anteriores</h3>
                  <div className="space-y-4">
                    {pastAppointments.map(appointment => (
                      <div key={appointment.id} className="border rounded-lg p-4 opacity-75">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Link
                                to={`/psicologo/${appointment.psychologist?.id || ''}`}
                                className="text-lg font-semibold text-gray-700"
                              >
                                {appointment.psychologist?.user?.nome_completo || 'Psicólogo não encontrado'}
                              </Link>
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                appointment.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {appointment.status === 'completed' ? 'Concluído' : 'Cancelado'}
                              </span>
                            </div>
                            <p className="text-gray-600 mb-1">
                              <Calendar className="inline mr-1" size={16} />
                              {formatDate(appointment.appointment_date)}
                            </p>
                          </div>
                          {appointment.status === 'completed' && appointment.psychologist?.id && (
                            <Link
                              to={`/psicologo/${appointment.psychologist.id}`}
                              className="btn-secondary text-sm px-4 py-2"
                            >
                              Avaliar
                            </Link>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {appointments.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">Você ainda não tem agendamentos</p>
                  <Link to="/buscar" className="btn-primary inline-flex items-center">
                    <Search className="mr-2" size={18} />
                    Buscar Psicólogos
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Favorites Tab */}
          {activeTab === 'favorites' && (
            <div className="space-y-4">
              {favorites.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">Você ainda não tem psicólogos favoritos</p>
                  <Link to="/buscar" className="btn-primary inline-flex items-center">
                    <Search className="mr-2" size={18} />
                    Buscar Psicólogos
                  </Link>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {favorites.map(psychologist => (
                    <div key={psychologist.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <Link
                          to={`/psicologo/${psychologist.id}`}
                          className="flex-1"
                        >
                          <h3 className="font-semibold text-gray-900 hover:text-primary-600">
                            {psychologist.user?.nome_completo || 'Nome não disponível'}
                          </h3>
                          <p className="text-sm text-gray-600">CRP: {psychologist.crp || 'N/A'}</p>
                        </Link>
                        <button
                          onClick={() => handleRemoveFavorite(psychologist.id)}
                          className="text-red-500 hover:text-red-700"
                          title="Remover dos favoritos"
                        >
                          <Heart className="fill-red-500" size={20} />
                        </button>
                      </div>
                      {psychologist.rating > 0 && (
                        <div className="flex items-center gap-1 mb-2">
                          <Star className="text-yellow-400 fill-yellow-400" size={16} />
                          <span className="text-sm font-medium">{psychologist.rating.toFixed(1)}</span>
                          <span className="text-xs text-gray-500">
                            ({psychologist.total_reviews})
                          </span>
                        </div>
                      )}
                      {psychologist.bio && (
                        <p className="text-sm text-gray-600 line-clamp-2">{psychologist.bio}</p>
                      )}
                      <Link
                        to={`/psicologo/${psychologist.id}`}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium mt-2 inline-block"
                      >
                        Ver perfil completo →
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Payment Form Modal */}
        {showPaymentForm && selectedAppointment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Pagamento</h2>
                <PaymentForm
                  appointment={selectedAppointment}
                  onSuccess={handlePaymentSuccess}
                  onCancel={() => {
                    setShowPaymentForm(false)
                    setSelectedAppointment(null)
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Cancel Confirmation Modal */}
        {cancelConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-orange-100 rounded-full">
                  <AlertTriangle className="text-orange-600" size={24} />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Cancelar Agendamento</h3>
              </div>
              <p className="text-gray-600 mb-2">
                Tem certeza que deseja cancelar este agendamento?
              </p>
              {cancelConfirm.psychologist?.user?.nome_completo && (
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Psicólogo:</span> {cancelConfirm.psychologist.user.nome_completo}
                  </p>
                  <p className="text-sm text-gray-700 mt-1">
                    <span className="font-medium">Data:</span> {formatDate(cancelConfirm.appointment_date)}
                  </p>
                </div>
              )}
              <p className="text-sm text-orange-600 mb-6">
                ⚠️ Esta ação não pode ser desfeita. O psicólogo será notificado sobre o cancelamento.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => handleCancelAppointment(cancelConfirm.id)}
                  className="btn-primary flex-1 bg-orange-600 hover:bg-orange-700 flex items-center justify-center"
                >
                  <XCircle className="mr-2" size={18} />
                  Confirmar Cancelamento
                </button>
                <button
                  onClick={() => setCancelConfirm(null)}
                  className="btn-secondary flex-1"
                >
                  Voltar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Ações Rápidas</h2>
          <div className="flex flex-wrap gap-4">
            <Link to="/pagamentos" className="btn-secondary flex items-center">
              <DollarSign className="mr-2" size={18} />
              Meus Pagamentos
            </Link>
            <Link to="/buscar" className="btn-primary inline-flex items-center">
              <Search className="mr-2" size={18} />
              Buscar Psicólogos
            </Link>
            <Link to="/dashboard" className="btn-secondary">
              Meu Perfil
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ClientDashboard

