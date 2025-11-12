import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../api/axios'
import { CreditCard, Calendar, User, CheckCircle, XCircle, Clock, DollarSign, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import PaymentForm from '../components/PaymentForm'

const Payments = () => {
  const { user } = useAuth()
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)
  const [appointments, setAppointments] = useState([])

  useEffect(() => {
    fetchPayments()
    fetchAppointments()
  }, [])

  const fetchPayments = async () => {
    try {
      const response = await api.get('/payments/my-payments')
      setPayments(response.data)
    } catch (error) {
      console.error('Erro ao carregar pagamentos:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/appointments/my-appointments')
      setAppointments(response.data)
    } catch (error) {
      console.error('Erro ao carregar agendamentos:', error)
    }
  }

  const handlePayAppointment = (appointment) => {
    setSelectedAppointment(appointment)
    setShowPaymentForm(true)
  }

  const handlePaymentSuccess = () => {
    setShowPaymentForm(false)
    setSelectedAppointment(null)
    fetchPayments()
    fetchAppointments()
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      paid: { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Pago' },
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock, text: 'Pendente' },
      failed: { color: 'bg-red-100 text-red-800', icon: XCircle, text: 'Falhou' },
      refunded: { color: 'bg-gray-100 text-gray-800', icon: XCircle, text: 'Reembolsado' }
    }

    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <Icon size={16} />
        {config.text}
      </span>
    )
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Agendamentos pendentes de pagamento
  const pendingAppointments = appointments.filter(
    apt => apt.status === 'confirmed' && apt.payment_status === 'pending'
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <Link to="/dashboard" className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="mr-2" size={20} />
            Voltar ao Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <DollarSign className="text-blue-600" size={32} />
            Meus Pagamentos
          </h1>
          <p className="text-gray-600 mt-2">Gerencie seus pagamentos e agendamentos</p>
        </div>

        {/* Agendamentos Pendentes de Pagamento */}
        {pendingAppointments.length > 0 && (
          <div className="card p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="text-yellow-600" size={24} />
              Agendamentos Pendentes de Pagamento
            </h2>
            <div className="space-y-4">
              {pendingAppointments.map(appointment => (
                <div key={appointment.id} className="border border-gray-200 rounded-lg p-4 bg-yellow-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <User className="text-gray-600" size={20} />
                        <h3 className="font-semibold text-gray-900">
                          {appointment.psychologist?.user?.full_name || 'Psicólogo'}
                        </h3>
                      </div>
                      <div className="flex items-center gap-3 mb-2 text-sm text-gray-600">
                        <Calendar className="text-gray-500" size={16} />
                        <span>
                          {new Date(appointment.appointment_date).toLocaleDateString('pt-BR', {
                            weekday: 'long',
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-blue-600">
                          {formatCurrency(appointment.psychologist?.consultation_price || 0)}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handlePayAppointment(appointment)}
                      className="btn-primary flex items-center"
                    >
                      <CreditCard className="mr-2" size={18} />
                      Pagar Agora
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Histórico de Pagamentos */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Histórico de Pagamentos</h2>
          
          {payments.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">Nenhum pagamento encontrado</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Data</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Psicólogo</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Método</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Valor</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">ID Transação</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map(payment => (
                    <tr key={payment.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-sm text-gray-700">
                        {formatDate(payment.created_at)}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-700">
                        {payment.appointment?.psychologist?.user?.full_name || 'N/A'}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-700 capitalize">
                        {payment.payment_method === 'credit_card' ? 'Cartão de Crédito' :
                         payment.payment_method === 'debit_card' ? 'Cartão de Débito' :
                         payment.payment_method === 'pix' ? 'PIX' :
                         payment.payment_method === 'boleto' ? 'Boleto' : payment.payment_method}
                      </td>
                      <td className="py-4 px-4 text-sm font-semibold text-gray-900">
                        {formatCurrency(payment.amount)}
                      </td>
                      <td className="py-4 px-4">
                        {getStatusBadge(payment.status)}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-500 font-mono">
                        {payment.transaction_id || payment.payment_id || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Payment Form Modal */}
        {showPaymentForm && selectedAppointment && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">Pagamento</h2>
                  <button
                    onClick={() => {
                      setShowPaymentForm(false)
                      setSelectedAppointment(null)
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle size={24} />
                  </button>
                </div>
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
      </div>
    </div>
  )
}

export default Payments

