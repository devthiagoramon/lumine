import { useState, useEffect } from 'react'
import { useToast } from '../../contexts/ToastContext'
import axios from 'axios'
import { CheckCircle, XCircle, User, Mail, Phone, MapPin, Briefcase, Star, AlertCircle, Loader, Ban, X } from 'lucide-react'

const PsychologistManagement = () => {
  const { success, error: showError, warning } = useToast()
  const [psychologists, setPsychologists] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending') // 'pending', 'verified', 'all'
  const [error, setError] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [modalType, setModalType] = useState(null) // 'verify', 'reject', 'unverify'
  const [selectedPsychologist, setSelectedPsychologist] = useState(null)
  const [reason, setReason] = useState('')
  const [reasonError, setReasonError] = useState('')

  useEffect(() => {
    fetchPsychologists()
  }, [filter])

  const fetchPsychologists = async () => {
    setLoading(true)
    setError('')
    try {
      let response
      if (filter === 'pending') {
        response = await axios.get('/api/admin/psychologists/pending')
        setPsychologists(response.data)
      } else {
        // Para verified e all, usar a rota normal de listagem
        response = await axios.get('/api/psychologists/')
        let data = response.data
        if (filter === 'verified') {
          data = data.filter(p => p.is_verified)
        }
        setPsychologists(data)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar psicólogos')
      console.error('Erro ao carregar psicólogos:', err)
    } finally {
      setLoading(false)
    }
  }

  const openModal = (type, psychologist) => {
    setModalType(type)
    setSelectedPsychologist(psychologist)
    setReason('')
    setReasonError('')
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setModalType(null)
    setSelectedPsychologist(null)
    setReason('')
    setReasonError('')
  }

  const handleVerify = async () => {
    if (!selectedPsychologist) return

    try {
      await axios.put(`/api/admin/psychologists/${selectedPsychologist.id}/verify`)
      fetchPsychologists()
      success('Psicólogo validado com sucesso')
      closeModal()
    } catch (err) {
      showError(err.response?.data?.detail || 'Erro ao validar psicólogo')
      console.error('Erro ao validar psicólogo:', err)
    }
  }

  const handleUnverify = async () => {
    if (!selectedPsychologist) return

    setReasonError('')
    if (!reason || reason.trim().length < 5) {
      setReasonError('É necessário informar um motivo com pelo menos 5 caracteres.')
      return
    }

    try {
      const motivo = encodeURIComponent(reason.trim())
      await axios.put(`/api/admin/psychologists/${selectedPsychologist.id}/unverify?motivo=${motivo}`)
      fetchPsychologists()
      success('Validação removida com sucesso')
      closeModal()
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erro ao remover validação'
      showError(errorMessage)
      console.error('Erro ao remover validação:', err)
      console.error('Detalhes do erro:', err.response?.data)
    }
  }

  const handleReject = async () => {
    if (!selectedPsychologist) return

    setReasonError('')
    if (!reason || reason.trim().length < 5) {
      setReasonError('É necessário informar um motivo com pelo menos 5 caracteres.')
      return
    }

    try {
      // Usar o endpoint unverify para rejeitar psicólogos pendentes
      const motivo = encodeURIComponent(reason.trim())
      await axios.put(`/api/admin/psychologists/${selectedPsychologist.id}/unverify?motivo=${motivo}`)
      fetchPsychologists()
      success('Psicólogo rejeitado com sucesso')
      closeModal()
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erro ao rejeitar psicólogo'
      showError(errorMessage)
      console.error('Erro ao rejeitar psicólogo:', err)
      console.error('Detalhes do erro:', err.response?.data)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'pending'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Pendentes ({filter === 'pending' ? psychologists.length : '...'})
        </button>
        <button
          onClick={() => setFilter('verified')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'verified'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Validados
        </button>
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todos
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-600">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : psychologists.length === 0 ? (
        <div className="text-center py-12">
          <User className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600 text-lg">
            {filter === 'pending' 
              ? 'Nenhum psicólogo pendente de validação'
              : 'Nenhum psicólogo encontrado'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {psychologists.map(psychologist => (
            <div
              key={psychologist.id}
              className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center text-white text-xl font-bold">
                      {psychologist.user.nome_completo.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">
                        {psychologist.user.nome_completo}
                      </h3>
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Mail size={14} />
                          {psychologist.user.email}
                        </span>
                        {psychologist.user.telefone && (
                          <span className="flex items-center gap-1">
                            <Phone size={14} />
                            {psychologist.user.telefone}
                          </span>
                        )}
                      </div>
                    </div>
                    {psychologist.is_verified ? (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium flex items-center gap-1">
                        <CheckCircle size={14} />
                        Validado
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium flex items-center gap-1">
                        <AlertCircle size={14} />
                        Pendente
                      </span>
                    )}
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">CRP</p>
                      <p className="font-medium text-gray-900">{psychologist.crp}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                        <Briefcase size={14} />
                        Experiência
                      </p>
                      <p className="font-medium text-gray-900">
                        {psychologist.experience_years !== undefined && psychologist.experience_years !== null 
                          ? psychologist.experience_years 
                          : 0} {((psychologist.experience_years !== undefined && psychologist.experience_years !== null ? psychologist.experience_years : 0) === 1) ? 'ano' : 'anos'}
                      </p>
                    </div>
                    {psychologist.city && psychologist.state && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                          <MapPin size={14} />
                          Localização
                        </p>
                        <p className="font-medium text-gray-900">
                          {psychologist.city}, {psychologist.state}
                        </p>
                      </div>
                    )}
                    {psychologist.rating > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                          <Star size={14} className="text-yellow-400 fill-yellow-400" />
                          Avaliação
                        </p>
                        <p className="font-medium text-gray-900">
                          {psychologist.rating.toFixed(1)} ({psychologist.total_reviews} avaliações)
                        </p>
                      </div>
                    )}
                  </div>

                  {psychologist.bio && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-1">Sobre</p>
                      <p className="text-gray-700 whitespace-pre-line">{psychologist.bio}</p>
                    </div>
                  )}

                  {psychologist.specialties.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm text-gray-600 mb-2">Especialidades</p>
                      <div className="flex flex-wrap gap-2">
                        {psychologist.specialties.map(spec => (
                          <span
                            key={spec.id}
                            className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs"
                          >
                            {spec.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Cadastrado em: {formatDate(psychologist.criado_em)}
                  </div>
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  {!psychologist.is_verified ? (
                    <>
                      <button
                        onClick={() => openModal('verify', psychologist)}
                        className="btn-primary flex items-center justify-center gap-2 whitespace-nowrap"
                      >
                        <CheckCircle size={18} />
                        Validar
                      </button>
                      <button
                        onClick={() => openModal('reject', psychologist)}
                        className="btn-secondary flex items-center justify-center gap-2 whitespace-nowrap bg-red-600 hover:bg-red-700 text-white"
                      >
                        <Ban size={18} />
                        Rejeitar
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => openModal('unverify', psychologist)}
                      className="btn-secondary flex items-center justify-center gap-2 whitespace-nowrap"
                    >
                      <XCircle size={18} />
                      Remover Validação
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Confirmação */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className={`p-6 border-b ${
              modalType === 'verify' ? 'bg-green-50 border-green-200' :
              modalType === 'reject' ? 'bg-red-50 border-red-200' :
              'bg-yellow-50 border-yellow-200'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {modalType === 'verify' && (
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="text-green-600" size={24} />
                    </div>
                  )}
                  {modalType === 'reject' && (
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                      <Ban className="text-red-600" size={24} />
                    </div>
                  )}
                  {modalType === 'unverify' && (
                    <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                      <XCircle className="text-yellow-600" size={24} />
                    </div>
                  )}
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {modalType === 'verify' && 'Validar Psicólogo'}
                      {modalType === 'reject' && 'Rejeitar Psicólogo'}
                      {modalType === 'unverify' && 'Remover Validação'}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {selectedPsychologist?.user?.nome_completo}
                    </p>
                  </div>
                </div>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="p-6">
              {modalType === 'verify' && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    Tem certeza que deseja validar o cadastro deste psicólogo? 
                    Ele poderá receber consultas e aparecerá nas buscas após a validação.
                  </p>
                </div>
              )}

              {(modalType === 'reject' || modalType === 'unverify') && (
                <div className="space-y-4">
                  <p className="text-gray-700">
                    {modalType === 'reject' 
                      ? 'Tem certeza que deseja rejeitar este psicólogo? Ele não poderá receber consultas até ser validado.'
                      : 'Tem certeza que deseja remover a validação deste psicólogo? Ele não poderá receber consultas até ser validado novamente.'}
                  </p>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Motivo {modalType === 'reject' ? 'da Rejeição' : 'para Remover Validação'} *
                    </label>
                    <textarea
                      value={reason}
                      onChange={(e) => {
                        setReason(e.target.value)
                        setReasonError('')
                      }}
                      rows={4}
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                        reasonError ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Informe o motivo..."
                    />
                    {reasonError && (
                      <p className="mt-1 text-sm text-red-600">{reasonError}</p>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      Mínimo de 5 caracteres
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  if (modalType === 'verify') {
                    handleVerify()
                  } else if (modalType === 'reject') {
                    handleReject()
                  } else if (modalType === 'unverify') {
                    handleUnverify()
                  }
                }}
                className={`px-4 py-2 text-white rounded-lg transition-colors ${
                  modalType === 'verify' 
                    ? 'bg-green-600 hover:bg-green-700' 
                    : modalType === 'reject'
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-yellow-600 hover:bg-yellow-700'
                }`}
              >
                {modalType === 'verify' && 'Confirmar Validação'}
                {modalType === 'reject' && 'Confirmar Rejeição'}
                {modalType === 'unverify' && 'Confirmar Remoção'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PsychologistManagement

