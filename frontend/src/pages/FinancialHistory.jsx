import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../api/axios'
import { DollarSign, TrendingUp, Wallet, ArrowLeft, Calendar, User, CheckCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

const FinancialHistory = () => {
  const { user } = useAuth()
  const [financialHistory, setFinancialHistory] = useState([])
  const [balance, setBalance] = useState(0)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalEarnings: 0,
    totalConsultations: 0,
    thisMonth: 0
  })

  useEffect(() => {
    fetchFinancialData()
  }, [])

  const fetchFinancialData = async () => {
    try {
      const [historyResponse, balanceResponse] = await Promise.all([
        api.get('/payments/financial-history'),
        api.get('/payments/balance')
      ])

      console.log('💰 DEBUG: Histórico financeiro recebido:', historyResponse.data)
      if (historyResponse.data && historyResponse.data.length > 0) {
        console.log('💰 DEBUG: Primeiro pagamento:', historyResponse.data[0])
        console.log('💰 DEBUG: Appointment do primeiro:', historyResponse.data[0].appointment)
        console.log('💰 DEBUG: User do appointment:', historyResponse.data[0].appointment?.user)
      }
      
      setFinancialHistory(historyResponse.data)
      setBalance(balanceResponse.data.balance || 0)

      // Calcular estatísticas
      const totalEarnings = historyResponse.data.reduce((sum, payment) => sum + (payment.amount * 0.80), 0)
      const thisMonth = new Date().getMonth()
      const thisYear = new Date().getFullYear()
      const thisMonthEarnings = historyResponse.data
        .filter(payment => {
          const paymentDate = new Date(payment.created_at || payment.criado_em)
          return paymentDate.getMonth() === thisMonth && paymentDate.getFullYear() === thisYear
        })
        .reduce((sum, payment) => sum + (payment.amount * 0.80), 0)

      setStats({
        totalEarnings,
        totalConsultations: historyResponse.data.length,
        thisMonth: thisMonthEarnings
      })
    } catch (error) {
      console.error('Erro ao carregar dados financeiros:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Data inválida'
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        console.error('Data inválida:', dateString)
        return 'Data inválida'
      }
      return date.toLocaleDateString('pt-BR', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      console.error('Erro ao formatar data:', error, dateString)
      return 'Data inválida'
    }
  }

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
            Histórico Financeiro
          </h1>
          <p className="text-gray-600 mt-2">Acompanhe seus ganhos e pagamentos recebidos</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Saldo Disponível</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(balance)}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Wallet className="text-blue-600" size={32} />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Ganho</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.totalEarnings)}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="text-green-600" size={32} />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Este Mês</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.thisMonth)}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-full">
                <Calendar className="text-yellow-600" size={32} />
              </div>
            </div>
          </div>
        </div>

        {/* Info sobre comissão */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">💡 Informação:</span> Você recebe 80% do valor de cada consulta. 
            Os 20% restantes são a comissão da plataforma.
          </p>
        </div>

        {/* Histórico */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Histórico de Pagamentos Recebidos</h2>
          
          {financialHistory.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600">Nenhum pagamento recebido ainda</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Data</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Cliente</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Valor Total</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Sua Parte (80%)</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Comissão (20%)</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {financialHistory.map(payment => {
                    const psychologistShare = payment.amount * 0.80
                    const platformFee = payment.amount * 0.20

                    return (
                      <tr key={payment.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-4 px-4 text-sm text-gray-700">
                          {formatDate(payment.created_at || payment.criado_em)}
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-700">
                          <div className="flex items-center gap-2">
                            <User className="text-gray-500" size={16} />
                            {payment.appointment?.user?.nome_completo || payment.appointment?.user?.full_name || 'N/A'}
                          </div>
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-700">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td className="py-4 px-4 text-sm font-semibold text-green-600">
                          {formatCurrency(psychologistShare)}
                        </td>
                        <td className="py-4 px-4 text-sm text-gray-500">
                          {formatCurrency(platformFee)}
                        </td>
                        <td className="py-4 px-4">
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            <CheckCircle size={16} />
                            Pago
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FinancialHistory

