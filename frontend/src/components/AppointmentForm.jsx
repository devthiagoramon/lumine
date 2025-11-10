import { useState } from 'react'
import axios from 'axios'
import { Calendar, Monitor, Building2, X } from 'lucide-react'

const AppointmentForm = ({ psychologist, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    appointment_date: '',
    appointment_type: 'online',
    notes: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const appointmentData = {
        psychologist_id: psychologist.id,
        appointment_date: new Date(formData.appointment_date).toISOString(),
        appointment_type: formData.appointment_type,
        notes: formData.notes || null
      }

      await axios.post('/api/appointments/', appointmentData)
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar agendamento')
    } finally {
      setLoading(false)
    }
  }

  // Definir data mínima como hoje
  const minDate = new Date().toISOString().slice(0, 16)

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Data e Hora *
        </label>
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="datetime-local"
            name="appointment_date"
            required
            min={minDate}
            value={formData.appointment_date}
            onChange={handleChange}
            className="input-field pl-10"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tipo de Consulta *
        </label>
        <div className="space-y-2">
          <label className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
            formData.appointment_type === 'online' && psychologist.online_consultation
              ? 'border-primary-600 bg-primary-50'
              : 'border-gray-200'
          } ${!psychologist.online_consultation ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <input
              type="radio"
              name="appointment_type"
              value="online"
              checked={formData.appointment_type === 'online'}
              onChange={handleChange}
              disabled={!psychologist.online_consultation}
              className="mr-3"
            />
            <Monitor className="mr-2 text-primary-600" size={20} />
            <div>
              <span className="font-medium">Online</span>
              {!psychologist.online_consultation && (
                <p className="text-xs text-gray-500">Não disponível</p>
              )}
            </div>
          </label>

          <label className={`flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
            formData.appointment_type === 'presencial' && psychologist.in_person_consultation
              ? 'border-primary-600 bg-primary-50'
              : 'border-gray-200'
          } ${!psychologist.in_person_consultation ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <input
              type="radio"
              name="appointment_type"
              value="presencial"
              checked={formData.appointment_type === 'presencial'}
              onChange={handleChange}
              disabled={!psychologist.in_person_consultation}
              className="mr-3"
            />
            <Building2 className="mr-2 text-primary-600" size={20} />
            <div>
              <span className="font-medium">Presencial</span>
              {!psychologist.in_person_consultation && (
                <p className="text-xs text-gray-500">Não disponível</p>
              )}
            </div>
          </label>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Observações (opcional)
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="input-field"
          placeholder="Alguma observação ou informação adicional..."
        />
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading || (!psychologist.online_consultation && !psychologist.in_person_consultation)}
          className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Agendando...' : 'Confirmar Agendamento'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary flex items-center"
        >
          <X className="mr-2" size={18} />
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default AppointmentForm

