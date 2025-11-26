import { useState, useEffect } from 'react'
import axios from 'axios'
import { Save, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const PsychologistProfileForm = ({ psychologist, onSuccess, onCancel }) => {
  const { user } = useAuth()
  const [formData, setFormData] = useState({
    crp: psychologist?.crp || '',
    bio: psychologist?.bio || '',
    experience_years: psychologist?.experience_years || 0,
    consultation_price: psychologist?.consultation_price || '',
    online_consultation: psychologist?.online_consultation ?? true,
    in_person_consultation: psychologist?.in_person_consultation ?? false,
    address: psychologist?.address || '',
    city: psychologist?.city || '',
    state: psychologist?.state || '',
    zip_code: psychologist?.zip_code || '',
    specialties_text: psychologist?.specialties?.map(s => s.name).join(', ') || '',
    approaches_text: psychologist?.approaches?.map(a => a.name).join(', ') || '',
    specialty_ids: [],
    approach_ids: [],
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Atualizar formData quando psychologist mudar
  useEffect(() => {
    if (psychologist) {
      setFormData({
        crp: psychologist.crp || '',
        bio: psychologist.bio || '',
        experience_years: psychologist.experience_years !== undefined && psychologist.experience_years !== null ? psychologist.experience_years : 0,
        consultation_price: psychologist.consultation_price || '',
        online_consultation: psychologist.online_consultation === true || psychologist.online_consultation === 'true',
        in_person_consultation: psychologist.in_person_consultation === true || psychologist.in_person_consultation === 'true',
        address: psychologist.address || '',
        city: psychologist.city || '',
        state: psychologist.state || '',
        zip_code: psychologist.zip_code || '',
        specialties_text: psychologist.specialties?.map(s => s.name).join(', ') || '',
        approaches_text: psychologist.approaches?.map(a => a.name).join(', ') || '',
        specialty_ids: [],
        approach_ids: [],
      })
    }
  }, [psychologist])

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }


  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Buscar IDs das especialidades e abordagens pelo nome
      let specialty_ids = []
      let approach_ids = []

      if (formData.specialties_text.trim()) {
        try {
          const specRes = await axios.get('/api/search/specialties')
          const specialtiesList = (specRes.data || []).filter(s => s && s.name) // Filtrar itens undefined/null
          const specialtiesNames = formData.specialties_text.split(',').map(s => s.trim()).filter(s => s)
          
          specialty_ids = specialtiesNames.map(name => {
            const found = specialtiesList.find(s => s && s.name && s.name.toLowerCase() === name.toLowerCase())
            return found ? found.id : null
          }).filter(id => id !== null)
        } catch (err) {
          console.error('Erro ao buscar especialidades:', err)
        }
      }

      if (formData.approaches_text.trim()) {
        try {
          const appRes = await axios.get('/api/search/approaches')
          const approachesList = (appRes.data || []).filter(a => a && a.name) // Filtrar itens undefined/null
          const approachesNames = formData.approaches_text.split(',').map(a => a.trim()).filter(a => a)
          
          approach_ids = approachesNames.map(name => {
            const found = approachesList.find(a => a && a.name && a.name.toLowerCase() === name.toLowerCase())
            return found ? found.id : null
          }).filter(id => id !== null)
        } catch (err) {
          console.error('Erro ao buscar abordagens:', err)
        }
      }

      // Garantir que experience_years seja sempre um número válido
      const experienceYearsValue = formData.experience_years
      const experienceYears = experienceYearsValue !== '' && experienceYearsValue !== null && experienceYearsValue !== undefined
        ? parseInt(experienceYearsValue)
        : 0
      
      // Garantir que os valores booleanos sejam sempre enviados explicitamente
      const onlineConsultation = formData.online_consultation === true || formData.online_consultation === 'true' || formData.online_consultation === 1
      const inPersonConsultation = formData.in_person_consultation === true || formData.in_person_consultation === 'true' || formData.in_person_consultation === 1
      
      // Garantir que os valores booleanos sejam sempre enviados explicitamente como boolean
      const data = {
        bio: formData.bio || null,
        experience_years: isNaN(experienceYears) ? 0 : experienceYears,
        consultation_price: formData.consultation_price && formData.consultation_price !== '' 
          ? parseFloat(formData.consultation_price) 
          : null,
        online_consultation: onlineConsultation,
        in_person_consultation: inPersonConsultation,
        address: formData.address || null,
        city: formData.city || null,
        state: formData.state || null,
        zip_code: formData.zip_code || null,
        specialty_ids: specialty_ids.length > 0 ? specialty_ids : [],
        approach_ids: approach_ids.length > 0 ? approach_ids : [],
      }
      
      // Adicionar CRP apenas se não for edição (para não tentar atualizar)
      if (!psychologist) {
        data.crp = formData.crp
      }
      
      console.log('Dados sendo enviados:', data)

      // Garantir que o token está sendo enviado
      const token = localStorage.getItem('token')
      if (!token) {
        setError('Você precisa estar logado para salvar o perfil. Redirecionando para login...')
        setTimeout(() => {
          window.location.href = '/login'
        }, 2000)
        return
      }
      
      // Configurar headers com o token
      const config = {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }

      if (psychologist) {
        await axios.put('/api/psychologists/me', data, config)
      } else {
        await axios.post('/api/psychologists/', data, config)
      }
      onSuccess()
    } catch (err) {
      console.error('Erro ao salvar perfil:', err)
      if (err.response?.status === 401) {
        setError('Sua sessão expirou. Por favor, faça login novamente.')
        localStorage.removeItem('token')
        // Redirecionar para login após 2 segundos
        setTimeout(() => {
          window.location.href = '/login'
        }, 2000)
      } else {
        setError(err.response?.data?.detail || 'Erro ao salvar perfil. Tente novamente.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          CRP (Conselho Regional de Psicologia) {!psychologist && '*'}
        </label>
        <input
          type="text"
          name="crp"
          required={!psychologist}
          value={formData.crp}
          onChange={handleChange}
          className="input-field"
          placeholder="Ex: 06/123456"
          readOnly={!!psychologist}
        />
        {psychologist && (
          <p className="text-xs text-gray-500 mt-1">
            O CRP não pode ser alterado após o cadastro
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Sobre você
        </label>
        <textarea
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows={5}
          className="input-field"
          placeholder="Conte um pouco sobre você, sua formação e experiência..."
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Anos de Experiência
          </label>
          <input
            type="number"
            name="experience_years"
            min="0"
            value={formData.experience_years}
            onChange={handleChange}
            className="input-field"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Valor da Consulta (R$)
          </label>
          <input
            type="number"
            name="consultation_price"
            min="0"
            step="0.01"
            value={formData.consultation_price}
            onChange={handleChange}
            className="input-field"
            placeholder="Ex: 150.00"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Tipos de Consulta
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              name="online_consultation"
              checked={formData.online_consultation}
              onChange={handleChange}
              className="mr-2"
            />
            <span>Consulta Online</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              name="in_person_consultation"
              checked={formData.in_person_consultation}
              onChange={handleChange}
              className="mr-2"
            />
            <span>Consulta Presencial</span>
          </label>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Endereço
          </label>
          <input
            type="text"
            name="address"
            value={formData.address}
            onChange={handleChange}
            className="input-field"
            placeholder="Rua, número"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cidade
          </label>
          <input
            type="text"
            name="city"
            value={formData.city}
            onChange={handleChange}
            className="input-field"
            placeholder="Ex: São Paulo"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estado
          </label>
          <input
            type="text"
            name="state"
            value={formData.state}
            onChange={handleChange}
            className="input-field"
            placeholder="Ex: SP"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CEP
          </label>
          <input
            type="text"
            name="zip_code"
            value={formData.zip_code}
            onChange={handleChange}
            className="input-field"
            placeholder="00000-000"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Especialidades
        </label>
        <input
          type="text"
          name="specialties_text"
          value={formData.specialties_text}
          onChange={handleChange}
          className="input-field"
          placeholder="Ex: Ansiedade, Depressão, TDAH (separadas por vírgula)"
        />
        <p className="text-xs text-gray-500 mt-1">
          Digite as especialidades separadas por vírgula
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Abordagens Terapêuticas
        </label>
        <input
          type="text"
          name="approaches_text"
          value={formData.approaches_text}
          onChange={handleChange}
          className="input-field"
          placeholder="Ex: TCC, Psicanálise, Humanista (separadas por vírgula)"
        />
        <p className="text-xs text-gray-500 mt-1">
          Digite as abordagens separadas por vírgula
        </p>
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary flex items-center disabled:opacity-50"
        >
          <Save className="mr-2" size={18} />
          {loading ? 'Salvando...' : 'Salvar'}
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

export default PsychologistProfileForm

