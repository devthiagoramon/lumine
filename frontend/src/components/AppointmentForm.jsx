import { useState, useEffect } from 'react'
import api from '../api/axios'
import { Monitor, Building2, X, Calendar as CalendarIcon, Clock } from 'lucide-react'
import AppointmentCalendar from './AppointmentCalendar'

const AppointmentForm = ({ psychologist, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    appointment_type: 'online',
    notes: ''
  })
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedTime, setSelectedTime] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState(1) // 1: Tipo e Calendário, 2: Confirmação

  // Resetar seleção quando mudar tipo de consulta
  useEffect(() => {
    setSelectedDate(null)
    setSelectedTime(null)
    setStep(1)
  }, [formData.appointment_type])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSlotSelect = (date, datetime) => {
    setSelectedDate(date)
    setSelectedTime(datetime)
    setError('')
  }

  const handleNext = () => {
    if (!selectedTime) {
      setError('Por favor, selecione uma data e horário')
      return
    }
    setStep(2)
  }

  const handleBack = () => {
    setStep(1)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Validar se a data foi preenchida
    if (!selectedTime) {
      setError('Por favor, selecione uma data e hora para o agendamento')
      setLoading(false)
      return
    }

    try {
      // Verificar se a data é válida e no futuro
      if (isNaN(selectedTime.getTime())) {
        setError('Data inválida. Por favor, selecione uma data válida.')
        setLoading(false)
        return
      }

      if (selectedTime <= new Date()) {
        setError('A data do agendamento deve ser no futuro')
        setLoading(false)
        return
      }

      const appointmentData = {
        psychologist_id: psychologist.id,
        appointment_date: selectedTime.toISOString(),
        appointment_type: formData.appointment_type,
        notes: formData.notes || null
      }

      await api.post('/appointments/', appointmentData)
      onSuccess()
    } catch (err) {
      console.error('Erro ao criar agendamento:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Erro ao criar agendamento'
      setError(errorMessage)
      console.error('Detalhes do erro:', err.response?.data)
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (date) => {
    if (!date) return ''
    return date.toLocaleString('pt-BR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      {step === 1 ? (
        <div className="space-y-6">
          {/* Tipo de Consulta */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tipo de Consulta *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                formData.appointment_type === 'online' && psychologist.online_consultation
                  ? 'border-blue-600 bg-blue-50 shadow-md'
                  : 'border-gray-200'
              } ${!psychologist.online_consultation ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-300'}`}>
                <input
                  type="radio"
                  name="appointment_type"
                  value="online"
                  checked={formData.appointment_type === 'online'}
                  onChange={handleChange}
                  disabled={!psychologist.online_consultation}
                  className="mr-3"
                />
                <Monitor className="mr-3 text-blue-600" size={24} />
                <div>
                  <span className="font-medium block">Online</span>
                  {!psychologist.online_consultation && (
                    <p className="text-xs text-gray-500">Não disponível</p>
                  )}
                </div>
              </label>

              <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                formData.appointment_type === 'presencial' && psychologist.in_person_consultation
                  ? 'border-blue-600 bg-blue-50 shadow-md'
                  : 'border-gray-200'
              } ${!psychologist.in_person_consultation ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-300'}`}>
                <input
                  type="radio"
                  name="appointment_type"
                  value="presencial"
                  checked={formData.appointment_type === 'presencial'}
                  onChange={handleChange}
                  disabled={!psychologist.in_person_consultation}
                  className="mr-3"
                />
                <Building2 className="mr-3 text-blue-600" size={24} />
                <div>
                  <span className="font-medium block">Presencial</span>
                  {!psychologist.in_person_consultation && (
                    <p className="text-xs text-gray-500">Não disponível</p>
                  )}
                </div>
              </label>
            </div>
          </div>

          {/* Calendário */}
          <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <CalendarIcon className="text-blue-600" size={24} />
              <h3 className="text-lg font-semibold text-gray-800">
                Selecione Data e Horário
              </h3>
            </div>
            
            <AppointmentCalendar
              psychologistId={psychologist.id}
              appointmentType={formData.appointment_type}
              onSelectSlot={handleSlotSelect}
              selectedDate={selectedDate}
              selectedTime={selectedTime}
            />
          </div>

          {/* Resumo da Seleção */}
          {selectedTime && (
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="text-blue-600" size={20} />
              <span className="font-semibold text-blue-800">Horário Selecionado:</span>
            </div>
            <p className="text-blue-700">{formatDateTime(selectedTime)}</p>
          </div>
          )}

          {/* Botões */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={onCancel}
              className="btn-secondary flex items-center"
            >
              <X className="mr-2" size={18} />
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleNext}
              disabled={!selectedTime || loading || (!psychologist.online_consultation && !psychologist.in_person_consultation)}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continuar
            </button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Resumo */}
          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Resumo do Agendamento</h3>
            
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <CalendarIcon className="text-primary-600 mt-1" size={20} />
                <div>
                  <p className="text-sm text-gray-600">Data e Horário</p>
                  <p className="font-medium text-gray-800">{formatDateTime(selectedTime)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                {formData.appointment_type === 'online' ? (
                  <Monitor className="text-blue-600 mt-1" size={20} />
                ) : (
                  <Building2 className="text-blue-600 mt-1" size={20} />
                )}
                <div>
                  <p className="text-sm text-gray-600">Tipo de Consulta</p>
                  <p className="font-medium text-gray-800 capitalize">
                    {formData.appointment_type === 'online' ? 'Online' : 'Presencial'}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full bg-primary-600 mt-1"></div>
                <div>
                  <p className="text-sm text-gray-600">Psicólogo</p>
                  <p className="font-medium text-gray-800">{psychologist.user?.full_name || 'Psicólogo'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Observações */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observações (opcional)
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={4}
              className="input-field w-full"
              placeholder="Alguma observação ou informação adicional que gostaria de compartilhar..."
            />
          </div>

          {/* Botões */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={handleBack}
              className="btn-secondary flex items-center"
            >
              Voltar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Agendando...' : 'Confirmar Agendamento'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

export default AppointmentForm
