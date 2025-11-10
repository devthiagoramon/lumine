import { useState, useEffect } from 'react'
import axios from 'axios'
import { Save, X } from 'lucide-react'

const PsychologistProfileForm = ({ psychologist, onSuccess, onCancel }) => {
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
    specialty_ids: psychologist?.specialties?.map(s => s.id) || [],
    approach_ids: psychologist?.approaches?.map(a => a.id) || [],
  })
  const [specialties, setSpecialties] = useState([])
  const [approaches, setApproaches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchOptions()
  }, [])

  const fetchOptions = async () => {
    try {
      const [specRes, appRes] = await Promise.all([
        axios.get('/api/search/specialties'),
        axios.get('/api/search/approaches')
      ])
      setSpecialties(specRes.data)
      setApproaches(appRes.data)
    } catch (error) {
      console.error('Erro ao carregar opções:', error)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleToggle = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(id => id !== value)
        : [...prev[field], value]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = {
        ...formData,
        consultation_price: formData.consultation_price ? parseFloat(formData.consultation_price) : null,
        experience_years: parseInt(formData.experience_years),
      }

      if (psychologist) {
        await axios.put('/api/psychologists/me', data)
      } else {
        await axios.post('/api/psychologists/', data)
      }
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar perfil')
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

      {!psychologist && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CRP (Conselho Regional de Psicologia) *
          </label>
          <input
            type="text"
            name="crp"
            required
            value={formData.crp}
            onChange={handleChange}
            className="input-field"
            placeholder="Ex: 06/123456"
          />
        </div>
      )}

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
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Especialidades
        </label>
        <div className="max-h-48 overflow-y-auto border rounded-lg p-3 space-y-2">
          {specialties.map(spec => (
            <label key={spec.id} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.specialty_ids.includes(spec.id)}
                onChange={() => handleToggle('specialty_ids', spec.id)}
                className="mr-2"
              />
              <span className="text-sm">{spec.name}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Abordagens Terapêuticas
        </label>
        <div className="max-h-48 overflow-y-auto border rounded-lg p-3 space-y-2">
          {approaches.map(approach => (
            <label key={approach.id} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.approach_ids.includes(approach.id)}
                onChange={() => handleToggle('approach_ids', approach.id)}
                className="mr-2"
              />
              <span className="text-sm">{approach.name}</span>
            </label>
          ))}
        </div>
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

