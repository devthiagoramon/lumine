import { useState, useEffect } from 'react'
import axios from 'axios'
import { Plus, Edit, Clock, Calendar, X, Save } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const AvailabilityManagement = () => {
  const { success, error: showError } = useToast()
  const [availabilities, setAvailabilities] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)

  const daysOfWeek = [
    { value: 0, label: 'Segunda-feira', short: 'Seg' },
    { value: 1, label: 'Terça-feira', short: 'Ter' },
    { value: 2, label: 'Quarta-feira', short: 'Qua' },
    { value: 3, label: 'Quinta-feira', short: 'Qui' },
    { value: 4, label: 'Sexta-feira', short: 'Sex' },
    { value: 5, label: 'Sábado', short: 'Sáb' },
    { value: 6, label: 'Domingo', short: 'Dom' }
  ]

  // Estado do formulário semanal
  const [weeklySchedule, setWeeklySchedule] = useState(() => {
    return daysOfWeek.map(day => ({
      day_of_week: day.value,
      label: day.label,
      short: day.short,
      enabled: false,
      start_time: '',
      end_time: '',
      existingId: null
    }))
  })

  useEffect(() => {
    fetchAvailabilities()
  }, [])

  const fetchAvailabilities = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/availability/')
      // Se a resposta for um array direto, usar; se for um objeto com data, usar data
      const availabilitiesData = Array.isArray(response.data) ? response.data : (response.data?.data || [])
      console.log('Disponibilidades recebidas:', availabilitiesData)
      setAvailabilities(availabilitiesData)
      
      // Preencher formulário com dados existentes
      const schedule = daysOfWeek.map(day => {
        const existing = availabilitiesData.find(a => a.day_of_week === day.value)
        return {
          day_of_week: day.value,
          label: day.label,
          short: day.short,
          enabled: !!existing && existing.is_available,
          start_time: existing?.start_time || '',
          end_time: existing?.end_time || '',
          existingId: existing?.id || null
        }
      })
      setWeeklySchedule(schedule)
    } catch (err) {
      console.error('Erro ao carregar disponibilidades:', err)
      console.error('Resposta completa:', err.response)
      showError('Erro ao carregar disponibilidades')
    } finally {
      setLoading(false)
    }
  }

  const handleDayChange = (dayIndex, field, value) => {
    setWeeklySchedule(prev => {
      const updated = [...prev]
      updated[dayIndex] = {
        ...updated[dayIndex],
        [field]: value
      }
      return updated
    })
  }

  const handleToggleDay = (dayIndex) => {
    setWeeklySchedule(prev => {
      const updated = [...prev]
      updated[dayIndex] = {
        ...updated[dayIndex],
        enabled: !updated[dayIndex].enabled,
        start_time: updated[dayIndex].enabled ? '' : updated[dayIndex].start_time,
        end_time: updated[dayIndex].enabled ? '' : updated[dayIndex].end_time
      }
      return updated
    })
  }

  const validateSchedule = () => {
    for (const day of weeklySchedule) {
      if (day.enabled) {
        if (!day.start_time || !day.end_time) {
          showError(`Preencha os horários para ${day.label}`)
          return false
        }
        if (day.start_time >= day.end_time) {
          showError(`O horário de fim deve ser posterior ao início em ${day.label}`)
          return false
        }
      }
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateSchedule()) {
      return
    }

    setSaving(true)
    try {
      const promises = []

      for (const day of weeklySchedule) {
        if (day.enabled) {
          // Criar ou atualizar
          if (day.existingId) {
            // Atualizar existente
            promises.push(
              axios.put(`/api/availability/${day.existingId}`, {
                start_time: day.start_time,
                end_time: day.end_time,
                is_available: true
              })
            )
          } else {
            // Criar novo
            promises.push(
              axios.post('/api/availability/', {
                day_of_week: day.day_of_week,
                start_time: day.start_time,
                end_time: day.end_time,
                is_available: true
              })
            )
          }
        } else if (day.existingId) {
          // Desativar existente (marcar como não disponível)
          promises.push(
            axios.put(`/api/availability/${day.existingId}`, {
              is_available: false
            })
          )
        }
      }

      await Promise.all(promises)
      success('Horários de disponibilidade salvos com sucesso!')
      
      // Pequeno delay para garantir que o backend processou tudo
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setShowForm(false)
      await fetchAvailabilities()
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Erro ao salvar disponibilidades'
      showError(errorMessage)
      console.error('Erro ao salvar disponibilidades:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir esta disponibilidade?')) {
      return
    }

    try {
      await axios.delete(`/api/availability/${id}`)
      success('Disponibilidade excluída com sucesso!')
      fetchAvailabilities()
    } catch (err) {
      showError(err.response?.data?.detail || 'Erro ao excluir disponibilidade')
    }
  }

  const getDayLabel = (dayOfWeek) => {
    const day = daysOfWeek.find(d => d.value === dayOfWeek)
    return day ? day.label : 'Desconhecido'
  }

  // Agrupar disponibilidades por dia da semana
  const groupedAvailabilities = availabilities.reduce((acc, avail) => {
    if (!acc[avail.day_of_week]) {
      acc[avail.day_of_week] = []
    }
    acc[avail.day_of_week].push(avail)
    return acc
  }, {})

  // Ordenar por dia da semana
  const sortedDays = Object.keys(groupedAvailabilities).sort((a, b) => parseInt(a) - parseInt(b))

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">Horários de Disponibilidade</h3>
          <p className="text-sm text-gray-600 mt-1">
            Configure seus horários de atendimento para cada dia da semana
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-primary flex items-center gap-2"
        >
          {showForm ? (
            <>
              <X size={18} />
              Cancelar
            </>
          ) : (
            <>
              <Edit size={18} />
              Editar Horários
            </>
          )}
        </button>
      </div>

      {/* Form Semanal */}
      {showForm && (
        <div className="card p-6 border-2 border-primary-200 mb-6">
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Configurar Horários da Semana
            </h4>
            <p className="text-sm text-gray-600">
              Marque os dias em que você trabalha e defina os horários de atendimento
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-3">
              {weeklySchedule.map((day, index) => (
                <div
                  key={day.day_of_week}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    day.enabled
                      ? 'border-primary-300 bg-primary-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {/* Checkbox para ativar/desativar dia */}
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id={`day-${day.day_of_week}`}
                        checked={day.enabled}
                        onChange={() => handleToggleDay(index)}
                        className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      />
                    </div>

                    {/* Label do dia */}
                    <label
                      htmlFor={`day-${day.day_of_week}`}
                      className={`flex-1 font-medium cursor-pointer ${
                        day.enabled ? 'text-gray-900' : 'text-gray-500'
                      }`}
                    >
                      {day.label}
                    </label>

                    {/* Campos de horário (só aparecem se o dia estiver ativado) */}
                    {day.enabled && (
                      <div className="flex items-center gap-3 flex-1">
                        <div className="flex-1">
                          <label className="block text-xs text-gray-600 mb-1">
                            Início
                          </label>
                          <input
                            type="time"
                            value={day.start_time}
                            onChange={(e) => handleDayChange(index, 'start_time', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            required={day.enabled}
                          />
                        </div>
                        <span className="text-gray-400 mt-5">até</span>
                        <div className="flex-1">
                          <label className="block text-xs text-gray-600 mb-1">
                            Fim
                          </label>
                          <input
                            type="time"
                            value={day.end_time}
                            onChange={(e) => handleDayChange(index, 'end_time', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            required={day.enabled}
                          />
                        </div>
                      </div>
                    )}

                    {!day.enabled && (
                      <span className="text-sm text-gray-400 italic">
                        Não trabalha neste dia
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 pt-4 border-t">
              <button
                type="submit"
                disabled={saving}
                className="btn-primary flex items-center gap-2 disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Salvando...
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    Salvar Horários
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  fetchAvailabilities() // Recarregar para resetar o formulário
                }}
                className="btn-secondary"
                disabled={saving}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Disponibilidades */}
      {!showForm && (
        <>
          {availabilities.filter(a => a.is_available).length === 0 ? (
            <div className="card p-12 text-center">
              <Calendar className="mx-auto text-gray-400 mb-4" size={48} />
              <p className="text-gray-600 text-lg mb-2">
                Nenhuma disponibilidade cadastrada
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Clique em "Editar Horários" para configurar seus horários de atendimento
              </p>
              <button
                onClick={() => setShowForm(true)}
                className="btn-primary inline-flex items-center gap-2"
              >
                <Plus size={18} />
                Configurar Horários
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {daysOfWeek.map(day => {
                const dayAvailabilities = availabilities.filter(
                  a => a.day_of_week === day.value && a.is_available
                )
                return (
                  <div key={day.value} className="card p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          dayAvailabilities.length > 0
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-400'
                        }`}>
                          <Calendar size={20} />
                        </div>
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900">
                            {day.label}
                          </h4>
                          {dayAvailabilities.length > 0 ? (
                            <div className="flex items-center gap-2 mt-1">
                              <Clock className="text-gray-500" size={16} />
                              <p className="text-sm text-gray-600">
                                {dayAvailabilities.map(a => `${a.start_time} - ${a.end_time}`).join(', ')}
                              </p>
                            </div>
                          ) : (
                            <p className="text-sm text-gray-400 italic">
                              Não trabalha neste dia
                            </p>
                          )}
                        </div>
                      </div>
                      {dayAvailabilities.length > 0 && (
                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                          Disponível
                        </span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AvailabilityManagement

