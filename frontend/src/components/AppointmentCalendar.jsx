import { useState, useEffect } from 'react'
import api from '../api/axios'
import { ChevronLeft, ChevronRight, Clock, Calendar as CalendarIcon, Loader2 } from 'lucide-react'

const AppointmentCalendar = ({ psychologistId, appointmentType, onSelectSlot, selectedDate, selectedTime }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [availableDates, setAvailableDates] = useState({})
  const [availableSlots, setAvailableSlots] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedDateState, setSelectedDateState] = useState(selectedDate || null)

  const daysOfWeek = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
  const months = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]

  // Buscar datas disponíveis ao mudar o mês
  useEffect(() => {
    if (psychologistId) {
      console.log('🔄 DEBUG: useEffect disparado - buscando datas disponíveis')
      console.log('🔄 DEBUG: psychologistId:', psychologistId)
      console.log('🔄 DEBUG: currentMonth:', currentMonth)
      console.log('🔄 DEBUG: appointmentType:', appointmentType)
      fetchAvailableDates()
    } else {
      console.warn('⚠️ DEBUG: psychologistId não está definido!')
    }
  }, [currentMonth, psychologistId, appointmentType])

  // Buscar horários quando uma data é selecionada
  useEffect(() => {
    if (selectedDateState) {
      fetchAvailableSlots(selectedDateState)
    } else {
      setAvailableSlots([])
    }
  }, [selectedDateState, psychologistId, appointmentType])

  const fetchAvailableDates = async () => {
    console.log('🚀 fetchAvailableDates CHAMADA!')
    console.log('🚀 psychologistId:', psychologistId)
    console.log('🚀 appointmentType:', appointmentType)
    
    if (!psychologistId) {
      console.error('❌ ERRO: psychologistId não está definido!')
      setAvailableDates({})
      return
    }
    
    setLoading(true)
    try {
      const startDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1)
      const endDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0)
      
      const startStr = startDate.toISOString().split('T')[0]
      const endStr = endDate.toISOString().split('T')[0]

      console.log(`📅 DEBUG: Buscando datas disponíveis para psicólogo ${psychologistId}, período: ${startStr} a ${endStr}`)
      console.log(`📅 DEBUG: URL completa: /api/availability/psychologist/${psychologistId}/available-dates`)
      console.log(`📅 DEBUG: Parâmetros:`, { start_date: startStr, end_date: endStr, appointment_type: appointmentType })
      
      console.log('📡 DEBUG: Fazendo requisição agora...')
      const response = await api.get(
        `/availability/psychologist/${psychologistId}/available-dates`,
        {
          params: {
            start_date: startStr,
            end_date: endStr,
            appointment_type: appointmentType
          }
        }
      )
      console.log('✅ DEBUG: Requisição concluída!')

      // Criar um objeto com as datas disponíveis
      console.log('✅ DEBUG: Requisição bem-sucedida!')
      console.log('✅ DEBUG: Status da resposta:', response.status)
      console.log('✅ DEBUG: Resposta completa do backend:', JSON.stringify(response.data, null, 2))
      console.log('✅ DEBUG: Available dates:', response.data.available_dates)
      console.log('✅ DEBUG: Tipo de available_dates:', typeof response.data.available_dates, Array.isArray(response.data.available_dates))
      
      if (!response.data || !response.data.available_dates) {
        console.warn('⚠️ ATENÇÃO: response.data.available_dates está vazio ou não existe!')
        console.warn('⚠️ response.data completo:', response.data)
      }
      
      const datesMap = {}
      if (response.data.available_dates && Array.isArray(response.data.available_dates)) {
        response.data.available_dates.forEach(dateInfo => {
          // Garantir que a data está no formato YYYY-MM-DD
          const dateKey = dateInfo.date ? dateInfo.date.split('T')[0] : dateInfo.date
          datesMap[dateKey] = dateInfo.count || 0
          console.log(`DEBUG: Adicionando data ao map: ${dateKey} = ${dateInfo.count}`)
        })
      }
      console.log('DEBUG: DatesMap criado:', datesMap)
      console.log('DEBUG: Chaves do DatesMap:', Object.keys(datesMap))
      setAvailableDates(datesMap)
    } catch (error) {
      console.error('❌ ERRO ao buscar datas disponíveis:', error)
      console.error('❌ Detalhes do erro:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          params: error.config?.params
        }
      })
      if (error.response) {
        console.error('❌ Resposta do servidor:', error.response.data)
      } else if (error.request) {
        console.error('❌ Requisição feita mas sem resposta do servidor')
      } else {
        console.error('❌ Erro ao configurar a requisição:', error.message)
      }
      setAvailableDates({})
    } finally {
      setLoading(false)
    }
  }

  const fetchAvailableSlots = async (date) => {
    console.log('🕐 fetchAvailableSlots CHAMADA para data:', date)
    setLoading(true)
    try {
      const dateStr = date.toISOString().split('T')[0]
      console.log('🕐 Buscando horários para:', dateStr)
      console.log('🕐 URL:', `/availability/psychologist/${psychologistId}/available-slots`)
      
      const response = await api.get(
        `/availability/psychologist/${psychologistId}/available-slots`,
        {
          params: {
            start_date: dateStr,
            end_date: dateStr,
            appointment_type: appointmentType
          }
        }
      )

      console.log('✅ Horários recebidos:', response.data)
      console.log('✅ Available slots:', response.data.available_slots)

      // Filtrar apenas os slots do dia selecionado e ordenar por horário
      const daySlots = response.data.available_slots
        .filter(slot => slot.date === dateStr)
        .sort((a, b) => a.time.localeCompare(b.time))
      
      console.log('✅ Slots filtrados para o dia:', daySlots)
      setAvailableSlots(daySlots)
    } catch (error) {
      console.error('❌ Erro ao buscar horários disponíveis:', error)
      console.error('❌ Detalhes:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      setAvailableSlots([])
    } finally {
      setLoading(false)
    }
  }

  const navigateMonth = (direction) => {
    setCurrentMonth(prev => {
      const newDate = new Date(prev)
      newDate.setMonth(prev.getMonth() + direction)
      return newDate
    })
  }

  const getDaysInMonth = () => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days = []
    
    // Dias do mês anterior (para preencher a primeira semana)
    const prevMonth = new Date(year, month - 1, 0)
    const prevMonthDays = prevMonth.getDate()
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthDays - i),
        isCurrentMonth: false,
        isToday: false,
        isSelected: false,
        isAvailable: false,
        availableCount: 0
      })
    }

    // Dias do mês atual
    const today = new Date()
    today.setHours(0, 0, 0, 0) // Normalizar para meia-noite para comparação
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day)
      date.setHours(0, 0, 0, 0) // Normalizar para meia-noite
      // Usar formato YYYY-MM-DD manualmente para evitar problemas de timezone
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      const isToday = date.getTime() === today.getTime()
      const isSelected = selectedDateState && dateStr === selectedDateState.toISOString().split('T')[0]
      const isAvailable = dateStr in availableDates
      const availableCount = availableDates[dateStr] || 0
      const isPast = date < today
      
      // Debug para segundas e terças
      if (date.getDay() === 1 || date.getDay() === 2) {
        console.log(`DEBUG Calendar: ${dateStr} (dia ${date.getDay()}), isAvailable: ${isAvailable}, count: ${availableCount}, availableDates keys:`, Object.keys(availableDates))
      }

      days.push({
        date,
        isCurrentMonth: true,
        isToday,
        isSelected,
        isAvailable: isAvailable && !isPast,
        availableCount,
        isPast
      })
    }

    // Dias do próximo mês (para completar a última semana)
    const remainingDays = 42 - days.length // 6 semanas * 7 dias
    for (let day = 1; day <= remainingDays; day++) {
      days.push({
        date: new Date(year, month + 1, day),
        isCurrentMonth: false,
        isToday: false,
        isSelected: false,
        isAvailable: false,
        availableCount: 0
      })
    }

    return days
  }

  const handleDateClick = (day) => {
    // Só permitir selecionar se não for passado, for do mês atual E tiver disponibilidade
    if (!day.isPast && day.isCurrentMonth && day.isAvailable) {
      setSelectedDateState(day.date)
      if (onSelectSlot) {
        onSelectSlot(null, null) // Limpar seleção de horário ao mudar data
      }
    }
  }

  const handleTimeClick = (slot) => {
    if (onSelectSlot && selectedDateState) {
      // Extrair horas e minutos do horário do slot (formato "HH:MM")
      const [hours, minutes] = slot.time.split(':').map(Number)
      
      // Criar datetime usando a data selecionada e o horário do slot
      // Usar getFullYear, getMonth, getDate para evitar problemas de timezone
      const year = selectedDateState.getFullYear()
      const month = selectedDateState.getMonth()
      const day = selectedDateState.getDate()
      
      const datetime = new Date(year, month, day, hours, minutes, 0, 0)
      
      console.log('🕐 Horário selecionado:', {
        slotTime: slot.time,
        hours: hours,
        minutes: minutes,
        selectedDate: `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
        createdDatetime: datetime.toISOString(),
        localHours: datetime.getHours(),
        localMinutes: datetime.getMinutes(),
        localString: datetime.toLocaleString('pt-BR', { 
          hour: '2-digit', 
          minute: '2-digit',
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        })
      })
      
      onSelectSlot(selectedDateState, datetime)
    }
  }

  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':')
    return `${hours}:${minutes}`
  }

  const days = getDaysInMonth()

  return (
    <div className="w-full">
      {/* Cabeçalho do Calendário */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigateMonth(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Mês anterior"
        >
          <ChevronLeft className="text-gray-600" size={24} />
        </button>
        
        <h3 className="text-xl font-semibold text-gray-800">
          {months[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h3>
        
        <button
          onClick={() => navigateMonth(1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Próximo mês"
        >
          <ChevronRight className="text-gray-600" size={24} />
        </button>
      </div>

      {/* Dias da Semana */}
      <div className="grid grid-cols-7 gap-2 mb-2">
        {daysOfWeek.map(day => (
          <div key={day} className="text-center text-sm font-medium text-gray-600 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendário */}
      {loading && !selectedDateState ? (
        <div className="text-center py-12 text-gray-500 flex items-center justify-center gap-2">
          <Loader2 className="animate-spin" size={24} />
          <span>Carregando calendário...</span>
        </div>
      ) : (
        <div className="grid grid-cols-7 gap-2 mb-6">
          {days.map((day, index) => {
            const dateStr = day.date.toISOString().split('T')[0]
            const isSelected = selectedDateState && dateStr === selectedDateState.toISOString().split('T')[0]
            
            return (
              <button
                key={index}
                onClick={() => handleDateClick(day)}
                disabled={day.isPast || !day.isCurrentMonth || !day.isAvailable}
                title={
                  day.isPast 
                    ? 'Data no passado' 
                    : !day.isCurrentMonth 
                    ? 'Dia de outro mês'
                    : !day.isAvailable
                    ? 'Psicólogo não trabalha neste dia'
                    : 'Selecionar data'
                }
                className={`
                  aspect-square p-2 rounded-lg text-sm font-medium transition-all
                  ${!day.isCurrentMonth ? 'text-gray-300 cursor-default' : ''}
                  ${day.isPast ? 'text-gray-300 cursor-not-allowed bg-gray-50' : ''}
                  ${!day.isAvailable && day.isCurrentMonth && !day.isPast ? 'text-gray-400 bg-gray-100 cursor-not-allowed border border-gray-200 opacity-60' : ''}
                  ${day.isToday && !isSelected && day.isCurrentMonth && !day.isPast && day.isAvailable ? 'bg-blue-50 text-blue-600 border-2 border-blue-200' : ''}
                  ${isSelected ? 'bg-blue-600 text-white shadow-lg scale-105' : ''}
                  ${!day.isPast && day.isCurrentMonth && day.isAvailable && !isSelected
                      ? 'hover:bg-blue-50 hover:text-blue-600 hover:border-2 hover:border-blue-200 cursor-pointer border border-transparent'
                      : ''
                  }
                  flex flex-col items-center justify-center relative
                `}
              >
                <span>{day.date.getDate()}</span>
                {day.isAvailable && day.availableCount > 0 && !day.isPast && (
                  <span className="text-xs mt-1 opacity-75">
                    {day.availableCount} {day.availableCount === 1 ? 'horário' : 'horários'}
                  </span>
                )}
                {!day.isAvailable && day.isCurrentMonth && !day.isPast && (
                  <span className="text-xs mt-1 opacity-50">
                    Indisponível
                  </span>
                )}
              </button>
            )
          })}
        </div>
      )}

      {/* Horários Disponíveis */}
      {selectedDateState && (
        <div className="mt-6 border-t pt-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="text-blue-600" size={20} />
            <h4 className="text-lg font-semibold text-gray-800">
              Horários disponíveis em {selectedDateState.toLocaleDateString('pt-BR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long'
              })}
            </h4>
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-500 flex items-center justify-center gap-2">
              <Loader2 className="animate-spin" size={20} />
              <span>Carregando horários...</span>
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {availableSlots.map((slot, index) => {
                // Comparar usando a data e o horário (HH:MM) ao invés do datetime completo
                const [slotHours, slotMinutes] = slot.time.split(':').map(Number)
                const selectedDateStr = selectedDateState?.toISOString().split('T')[0]
                const slotDateStr = slot.date
                
                // Criar um datetime de referência para comparação usando o horário do slot
                const slotDateTime = new Date(selectedDateState)
                slotDateTime.setHours(slotHours, slotMinutes, 0, 0)
                
                const isSelected = selectedTime && 
                  selectedDateStr === slotDateStr &&
                  selectedTime.getHours() === slotHours &&
                  selectedTime.getMinutes() === slotMinutes
                
                console.log('🔍 Comparando horário:', {
                  slotTime: slot.time,
                  slotHours,
                  slotMinutes,
                  selectedTimeHours: selectedTime?.getHours(),
                  selectedTimeMinutes: selectedTime?.getMinutes(),
                  isSelected,
                  selectedDateStr,
                  slotDateStr
                })
                
                return (
                  <button
                    key={index}
                    onClick={() => handleTimeClick(slot)}
                    className={`
                      p-3 rounded-lg border-2 transition-all text-sm font-medium
                      ${isSelected
                        ? 'bg-blue-600 text-white border-blue-600 shadow-lg'
                        : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                      }
                    `}
                  >
                    {formatTime(slot.time)}
                  </button>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CalendarIcon className="mx-auto mb-2 text-gray-400" size={32} />
              <p className="font-medium mb-1">Nenhum horário disponível para esta data</p>
              <p className="text-sm text-gray-400">
                Este psicólogo pode não ter horários configurados para este dia da semana.
              </p>
            </div>
          )}
        </div>
      )}

      {!selectedDateState && (
        <div className="text-center py-8 text-gray-500">
          <CalendarIcon className="mx-auto mb-2 text-gray-400" size={32} />
          <p>Selecione uma data para ver os horários disponíveis</p>
        </div>
      )}
    </div>
  )
}

export default AppointmentCalendar

