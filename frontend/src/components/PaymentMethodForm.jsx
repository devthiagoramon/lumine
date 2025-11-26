import { useState, useEffect } from 'react'
import { CreditCard, X, AlertCircle } from 'lucide-react'
import api from '../api/axios'

const PaymentMethodForm = ({ method, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    card_type: 'credit_card',
    card_number: '',
    card_holder: '',
    card_expiry: '',
    card_cvv: '',
    is_default: false
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (method) {
      // Modo edição - preencher com dados existentes (sem número completo e CVV por segurança)
      setFormData({
        card_type: method.card_type,
        card_number: '', // Não mostramos o número completo por segurança
        card_holder: method.card_holder,
        card_expiry: `${method.expiry_month}/${method.expiry_year.slice(-2)}`,
        card_cvv: '', // Não mostramos o CVV por segurança
        is_default: method.is_default
      })
    }
  }, [method])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
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
    setLoading(true)

    try {
      // Validações
      if (!formData.card_number || formData.card_number.replace(/\s/g, '').length < 13) {
        setError('Número do cartão inválido')
        setLoading(false)
        return
      }
      if (!formData.card_holder) {
        setError('Nome do portador é obrigatório')
        setLoading(false)
        return
      }
      if (!formData.card_expiry || !/^\d{2}\/\d{2}$/.test(formData.card_expiry)) {
        setError('Data de validade inválida (use MM/AA)')
        setLoading(false)
        return
      }
      if (!formData.card_cvv || formData.card_cvv.length < 3) {
        setError('CVV inválido')
        setLoading(false)
        return
      }

      if (method) {
        // Atualizar método existente
        const updateData = {
          card_holder: formData.card_holder,
          card_expiry: formData.card_expiry,
          is_default: formData.is_default
        }
        await api.put(`/payment-methods/${method.id}`, updateData)
      } else {
        // Criar novo método
        const payload = {
          card_type: formData.card_type,
          card_number: formData.card_number.replace(/\s/g, ''),
          card_holder: formData.card_holder,
          card_expiry: formData.card_expiry,
          card_cvv: formData.card_cvv,
          is_default: formData.is_default
        }
        console.log('📤 Enviando dados para criar método de pagamento:', {
          ...payload,
          card_number: payload.card_number.substring(0, 4) + '...' + payload.card_number.substring(payload.card_number.length - 4),
          card_cvv: '***'
        })
        await api.post('/payment-methods/', payload)
      }

      onSuccess()
    } catch (err) {
      console.error('❌ Erro ao salvar método de pagamento:', err)
      console.error('❌ Response data:', err.response?.data)
      
      // Tratar erros de validação (422) que vêm como array
      let errorMessage = 'Erro ao salvar método de pagamento'
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          // Se for array de erros de validação, pegar a primeira mensagem
          errorMessage = err.response.data.detail[0]?.msg || err.response.data.detail[0]?.message || errorMessage
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="text-red-600 mr-2 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {!method && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Cartão *
          </label>
          <select
            name="card_type"
            required
            value={formData.card_type}
            onChange={handleChange}
            className="input-field"
          >
            <option value="credit_card">Cartão de Crédito</option>
            <option value="debit_card">Cartão de Débito</option>
          </select>
        </div>
      )}

      {!method && (
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
      )}

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

        {!method && (
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
        )}
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          name="is_default"
          id="is_default"
          checked={formData.is_default}
          onChange={handleChange}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="is_default" className="ml-2 block text-sm text-gray-700">
          Definir como método de pagamento padrão
        </label>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex-1 flex items-center justify-center disabled:opacity-50"
        >
          {loading ? 'Salvando...' : (method ? 'Atualizar' : 'Adicionar Cartão')}
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

export default PaymentMethodForm



