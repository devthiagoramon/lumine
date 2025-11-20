import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../api/axios'
import { CreditCard, Calendar, User, CheckCircle, XCircle, Clock, DollarSign, ArrowLeft, Plus, Edit, Trash2, Star, Shield, MoreVertical } from 'lucide-react'
import { Link } from 'react-router-dom'
import PaymentForm from '../components/PaymentForm'
import PaymentMethodForm from '../components/PaymentMethodForm'

const Payments = () => {
  const { user } = useAuth()
  const [payments, setPayments] = useState([])
  const [paymentMethods, setPaymentMethods] = useState([])
  const [loading, setLoading] = useState(true)
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [showMethodForm, setShowMethodForm] = useState(false)
  const [selectedAppointment, setSelectedAppointment] = useState(null)
  const [selectedMethod, setSelectedMethod] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [openMenuId, setOpenMenuId] = useState(null)

  useEffect(() => {
    fetchPayments()
    fetchAppointments()
    fetchPaymentMethods()
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

  const fetchPaymentMethods = async () => {
    try {
      const response = await api.get('/payment-methods/')
      setPaymentMethods(response.data)
    } catch (error) {
      console.error('Erro ao carregar métodos de pagamento:', error)
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

  const handleMethodSuccess = () => {
    setShowMethodForm(false)
    setSelectedMethod(null)
    fetchPaymentMethods()
  }

  const handleAddMethod = () => {
    setSelectedMethod(null)
    setShowMethodForm(true)
  }

  const handleEditMethod = (method) => {
    setSelectedMethod(method)
    setShowMethodForm(true)
  }

  const handleSetDefault = async (methodId) => {
    try {
      await api.post(`/payment-methods/${methodId}/definir-padrao`)
      fetchPaymentMethods()
    } catch (error) {
      console.error('Erro ao definir método como padrão:', error)
    }
  }

  const handleDeleteMethod = async (methodId) => {
    try {
      await api.delete(`/payment-methods/${methodId}`)
      setDeleteConfirm(null)
      fetchPaymentMethods()
    } catch (error) {
      console.error('Erro ao deletar método:', error)
    }
  }

  const getCardBrandIcon = (brand) => {
    const brandColors = {
      visa: 'text-blue-600',
      mastercard: 'text-red-600',
      amex: 'text-blue-500',
      elo: 'text-orange-600',
      unknown: 'text-gray-600'
    }
    return brandColors[brand] || brandColors.unknown
  }

  const getCardBrandName = (brand) => {
    const brandNames = {
      visa: 'Visa',
      mastercard: 'Mastercard',
      amex: 'American Express',
      elo: 'Elo',
      unknown: 'Cartão'
    }
    return brandNames[brand] || brandNames.unknown
  }

  const getCardBrandLogo = (brand) => {
    const brandStyles = {
      visa: {
        bg: 'bg-blue-600',
        text: 'text-white',
        label: 'VISA'
      },
      mastercard: {
        bg: 'bg-gradient-to-r from-red-600 to-orange-500',
        text: 'text-white',
        label: 'MC'
      },
      amex: {
        bg: 'bg-blue-500',
        text: 'text-white',
        label: 'AMEX'
      },
      elo: {
        bg: 'bg-yellow-400',
        text: 'text-gray-900',
        label: 'ELO'
      },
      unknown: {
        bg: 'bg-gray-300',
        text: 'text-gray-600',
        label: '•••'
      }
    }
    
    const style = brandStyles[brand] || brandStyles.unknown
    
    return (
      <div className={`w-16 h-10 ${style.bg} rounded flex items-center justify-center shadow-sm`}>
        <span className={`text-xs font-bold ${style.text}`}>{style.label}</span>
      </div>
    )
  }

  const handleMenuToggle = (methodId) => {
    setOpenMenuId(openMenuId === methodId ? null : methodId)
  }

  const handleMenuAction = (action, method) => {
    setOpenMenuId(null)
    if (action === 'setDefault') {
      handleSetDefault(method.id)
    } else if (action === 'delete') {
      setDeleteConfirm(method.id)
    }
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

        {/* Gerenciamento de Métodos de Pagamento */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <CreditCard className="text-blue-600" size={24} />
              Métodos de Pagamento
            </h2>
            <button
              onClick={handleAddMethod}
              className="btn-primary flex items-center"
            >
              <Plus className="mr-2" size={18} />
              Adicionar Cartão
            </button>
          </div>

          {paymentMethods.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
              <CreditCard className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600 mb-4">Nenhum cartão cadastrado</p>
            </div>
          ) : (
            <div className="space-y-3">
              {paymentMethods.map(method => (
                <div
                  key={method.id}
                  className={`border rounded-lg p-4 transition-all ${
                    method.is_default
                      ? 'border-blue-500 bg-blue-50 shadow-sm'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      {/* Ícone da Bandeira */}
                      <div className="flex-shrink-0">
                        {getCardBrandLogo(method.card_brand)}
                      </div>
                      
                      {/* Informações do Cartão */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900">
                            {getCardBrandName(method.card_brand)}
                          </h3>
                          {method.is_default && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                              <Star size={10} fill="currentColor" />
                              Padrão
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-gray-600">
                          <span className="font-medium">
                            {method.card_type === 'credit_card' ? 'Crédito' : 'Débito'}
                          </span>
                          <span>•••• {method.last_four_digits}</span>
                          <span>Validade: {method.expiry_month}/{method.expiry_year.slice(-2)}</span>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{method.card_holder}</p>
                      </div>
                    </div>

                    {/* Menu de Ações */}
                    <div className="relative flex-shrink-0 ml-4">
                      <button
                        onClick={() => handleMenuToggle(method.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                        title="Opções"
                      >
                        <MoreVertical size={20} />
                      </button>
                      
                      {openMenuId === method.id && (
                        <>
                          <div
                            className="fixed inset-0 z-10"
                            onClick={() => setOpenMenuId(null)}
                          />
                          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                            {!method.is_default && (
                              <button
                                onClick={() => handleMenuAction('setDefault', method)}
                                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                              >
                                <Star size={16} />
                                Tornar Padrão
                              </button>
                            )}
                            <button
                              onClick={() => handleMenuAction('delete', method)}
                              className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                            >
                              <Trash2 size={16} />
                              Remover
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Histórico de Pagamentos */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Histórico de Pagamentos</h2>
          
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
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Descrição/Serviço</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Método</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Valor</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map(payment => (
                    <tr key={payment.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="py-4 px-4 text-sm text-gray-700">
                        <div className="flex flex-col">
                          <span className="font-medium">
                            {new Date(payment.created_at).toLocaleDateString('pt-BR', {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric'
                            })}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(payment.created_at).toLocaleTimeString('pt-BR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex flex-col">
                          <span className="text-sm font-medium text-gray-900">
                            Consulta com {payment.appointment?.psychologist?.user?.full_name || 'Psicólogo'}
                          </span>
                          <span className="text-xs text-gray-500 mt-1">
                            {payment.appointment?.appointment_date && 
                              new Date(payment.appointment.appointment_date).toLocaleDateString('pt-BR', {
                                day: '2-digit',
                                month: 'long',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })
                            }
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-700">
                        <div className="flex items-center gap-2">
                          {payment.payment_method === 'credit_card' || payment.payment_method === 'debit_card' ? (
                            <CreditCard size={16} className="text-gray-400" />
                          ) : null}
                          <span className="capitalize">
                            {payment.payment_method === 'credit_card' ? 'Cartão de Crédito' :
                             payment.payment_method === 'debit_card' ? 'Cartão de Débito' :
                             payment.payment_method === 'pix' ? 'PIX' :
                             payment.payment_method === 'boleto' ? 'Boleto' : payment.payment_method}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-sm font-semibold text-gray-900">
                          {formatCurrency(payment.amount)}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        {getStatusBadge(payment.status)}
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

        {/* Payment Method Form Modal */}
        {showMethodForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedMethod ? 'Editar Método de Pagamento' : 'Adicionar Novo Cartão'}
                  </h2>
                  <button
                    onClick={() => {
                      setShowMethodForm(false)
                      setSelectedMethod(null)
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle size={24} />
                  </button>
                </div>
                <PaymentMethodForm
                  method={selectedMethod}
                  onSuccess={handleMethodSuccess}
                  onCancel={() => {
                    setShowMethodForm(false)
                    setSelectedMethod(null)
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-red-100 rounded-full">
                  <Trash2 className="text-red-600" size={24} />
                </div>
                <h3 className="text-xl font-bold text-gray-900">Remover Método de Pagamento</h3>
              </div>
              <p className="text-gray-600 mb-6">
                Tem certeza que deseja remover este método de pagamento? Esta ação não pode ser desfeita.
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => handleDeleteMethod(deleteConfirm)}
                  className="btn-primary flex-1 bg-red-600 hover:bg-red-700"
                >
                  Remover
                </button>
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="btn-secondary flex-1"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Payments

