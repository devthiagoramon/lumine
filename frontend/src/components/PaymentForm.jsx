import { useState } from 'react'
import axios from 'axios'
import { CreditCard, X, CheckCircle, AlertCircle } from 'lucide-react'

const PaymentForm = ({ appointment, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    payment_method: 'credit_card',
    card_number: '',
    card_holder: '',
    card_expiry: '',
    card_cvv: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '')
    const matches = v.match(/\d{4,16}/g)
    const match = matches && matches[0] || ''
    const parts = []
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4))
    }
    if (parts.length) {
      return parts.join(' ')
    } else {
      return v
    }
  }

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value)
    setFormData(prev => ({
      ...prev,
      card_number: formatted
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    // Validações básicas
    if (formData.payment_method === 'credit_card' || formData.payment_method === 'debit_card') {
      if (!formData.card_number || formData.card_number.replace(/\s/g, '').length < 13) {
        setError('Número do cartão inválido')
        return
      }
      if (!formData.card_holder) {
        setError('Nome do portador é obrigatório')
        return
      }
      if (!formData.card_expiry || !/^\d{2}\/\d{2}$/.test(formData.card_expiry)) {
        setError('Data de validade inválida (use MM/AA)')
        return
      }
      if (!formData.card_cvv || formData.card_cvv.length < 3) {
        setError('CVV inválido')
        return
      }
    }

    setLoading(true)

    try {
      const paymentData = {
        appointment_id: appointment.id,
        payment_method: formData.payment_method,
        ...(formData.payment_method === 'credit_card' || formData.payment_method === 'debit_card' ? {
          card_number: formData.card_number.replace(/\s/g, ''),
          card_holder: formData.card_holder,
          card_expiry: formData.card_expiry,
          card_cvv: formData.card_cvv
        } : {})
      }

      const response = await axios.post('/api/payments/', paymentData)
      
      if (response.data.status === 'paid') {
        setSuccess(true)
        setTimeout(() => {
          onSuccess()
        }, 2000)
      } else {
        setError('Pagamento falhou. Tente novamente.')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao processar pagamento')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="mx-auto text-green-600 mb-4" size={64} />
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Pagamento Processado!
        </h3>
        <p className="text-gray-600">
          Seu pagamento foi processado com sucesso.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="text-red-600 mr-2 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-4">
        <p className="text-sm text-gray-700 mb-1">
          <span className="font-medium">Valor:</span> R$ {appointment.psychologist.consultation_price?.toFixed(2) || '0.00'}
        </p>
        <p className="text-sm text-gray-700">
          <span className="font-medium">Psicólogo:</span> {appointment.psychologist.user.full_name}
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Método de Pagamento *
        </label>
        <select
          name="payment_method"
          required
          value={formData.payment_method}
          onChange={handleChange}
          className="input-field"
        >
          <option value="credit_card">Cartão de Crédito</option>
          <option value="debit_card">Cartão de Débito</option>
          <option value="pix">PIX</option>
          <option value="boleto">Boleto</option>
        </select>
      </div>

      {(formData.payment_method === 'credit_card' || formData.payment_method === 'debit_card') && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número do Cartão *
            </label>
            <div className="relative">
              <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                name="card_number"
                required
                value={formData.card_number}
                onChange={handleCardNumberChange}
                maxLength={19}
                placeholder="0000 0000 0000 0000"
                className="input-field pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Portador *
            </label>
            <input
              type="text"
              name="card_holder"
              required
              value={formData.card_holder}
              onChange={handleChange}
              placeholder="NOME COMO NO CARTÃO"
              className="input-field uppercase"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Validade (MM/AA) *
              </label>
              <input
                type="text"
                name="card_expiry"
                required
                value={formData.card_expiry}
                onChange={(e) => {
                  let value = e.target.value.replace(/\D/g, '')
                  if (value.length >= 2) {
                    value = value.slice(0, 2) + '/' + value.slice(2, 4)
                  }
                  setFormData(prev => ({ ...prev, card_expiry: value }))
                }}
                maxLength={5}
                placeholder="MM/AA"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CVV *
              </label>
              <input
                type="text"
                name="card_cvv"
                required
                value={formData.card_cvv}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 4)
                  setFormData(prev => ({ ...prev, card_cvv: value }))
                }}
                maxLength={4}
                placeholder="123"
                className="input-field"
              />
            </div>
          </div>
        </>
      )}

      {formData.payment_method === 'pix' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-gray-700">
            O QR Code do PIX será gerado após confirmar o pagamento.
          </p>
        </div>
      )}

      {formData.payment_method === 'boleto' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-gray-700">
            O boleto será gerado após confirmar o pagamento.
          </p>
        </div>
      )}

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <p className="text-xs text-gray-600">
          ⚠️ Este é um sistema de pagamento mockado para demonstração. Nenhum valor real será cobrado.
        </p>
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50"
        >
          {loading ? 'Processando...' : (
            <>
              <CreditCard className="mr-2" size={18} />
              Confirmar Pagamento
            </>
          )}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary flex items-center"
          >
            <X className="mr-2" size={18} />
            Cancelar
          </button>
        )}
      </div>
    </form>
  )
}

export default PaymentForm

