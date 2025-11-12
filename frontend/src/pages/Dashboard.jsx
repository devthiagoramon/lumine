import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { User, Edit, Plus, Briefcase, Star, MapPin, Monitor, Building2 } from 'lucide-react'
import PsychologistProfileForm from '../components/PsychologistProfileForm'

const Dashboard = () => {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [psychologist, setPsychologist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login')
    } else if (user && user.is_psychologist) {
      fetchPsychologistProfile()
    } else {
      setLoading(false)
    }
  }, [user, authLoading, navigate])

  const fetchPsychologistProfile = async () => {
    try {
      const response = await axios.get('/api/psychologists/me')
      setPsychologist(response.data)
    } catch (error) {
      if (error.response?.status !== 404) {
        console.error('Erro ao carregar perfil:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleProfileCreated = () => {
    setShowForm(false)
    fetchPsychologistProfile()
  }

  const handleProfileUpdated = () => {
    setEditing(false)
    fetchPsychologistProfile()
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Meu Perfil
          </h1>
          <p className="text-gray-600">
            Gerencie suas informações e perfil profissional
          </p>
        </div>

        {/* User Info */}
        <div className="card p-8 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center text-white text-3xl font-bold">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user.full_name}</h2>
                <p className="text-gray-600">{user.email}</p>
                {user.phone && <p className="text-gray-600">{user.phone}</p>}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <User className="text-primary-600" size={24} />
              <span className="text-sm font-medium text-gray-700">
                {user.is_psychologist ? 'Psicólogo' : 'Paciente'}
              </span>
            </div>
            <div className="flex gap-3 mt-4">
              {user.is_psychologist ? (
                <Link to="/dashboard/psicologo" className="btn-primary">
                  Ver Dashboard Completo
                </Link>
              ) : (
                <Link to="/dashboard/cliente" className="btn-primary">
                  Ver Dashboard Completo
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Psychologist Profile */}
        {user.is_psychologist && (
          <div className="card p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Perfil Profissional</h2>
              {psychologist ? (
                <button
                  onClick={() => setEditing(!editing)}
                  className="btn-secondary flex items-center"
                >
                  <Edit className="mr-2" size={18} />
                  {editing ? 'Cancelar' : 'Editar'}
                </button>
              ) : (
                <button
                  onClick={() => setShowForm(true)}
                  className="btn-primary flex items-center"
                >
                  <Plus className="mr-2" size={18} />
                  Criar Perfil
                </button>
              )}
            </div>

            {showForm && !psychologist && (
              <PsychologistProfileForm
                onSuccess={handleProfileCreated}
                onCancel={() => setShowForm(false)}
              />
            )}

            {editing && psychologist && (
              <PsychologistProfileForm
                psychologist={psychologist}
                onSuccess={handleProfileUpdated}
                onCancel={() => setEditing(false)}
              />
            )}

            {!showForm && !editing && psychologist && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">CRP</h3>
                  <p className="text-gray-700">{psychologist.crp}</p>
                </div>

                {psychologist.bio && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Sobre</h3>
                    <p className="text-gray-700 whitespace-pre-line">{psychologist.bio}</p>
                  </div>
                )}

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <Briefcase className="mr-2 text-primary-600" size={20} />
                      Experiência
                    </h3>
                    <p className="text-gray-700">
                      {psychologist.experience_years} {psychologist.experience_years === 1 ? 'ano' : 'anos'}
                    </p>
                  </div>

                  {psychologist.consultation_price && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Valor da Consulta</h3>
                      <p className="text-gray-700 text-2xl font-bold text-primary-600">
                        R$ {psychologist.consultation_price.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>

                {psychologist.city && psychologist.state && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <MapPin className="mr-2 text-primary-600" size={20} />
                      Localização
                    </h3>
                    <p className="text-gray-700">
                      {psychologist.city}, {psychologist.state}
                      {psychologist.address && ` - ${psychologist.address}`}
                    </p>
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Tipos de Consulta</h3>
                  <div className="flex gap-4">
                    {psychologist.online_consultation && (
                      <div className="flex items-center text-gray-700">
                        <Monitor className="mr-2 text-primary-600" size={20} />
                        <span>Online</span>
                      </div>
                    )}
                    {psychologist.in_person_consultation && (
                      <div className="flex items-center text-gray-700">
                        <Building2 className="mr-2 text-primary-600" size={20} />
                        <span>Presencial</span>
                      </div>
                    )}
                  </div>
                </div>

                {psychologist.specialties.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Especialidades</h3>
                    <div className="flex flex-wrap gap-2">
                      {psychologist.specialties.map(spec => (
                        <span
                          key={spec.id}
                          className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                        >
                          {spec.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {psychologist.approaches.length > 0 && (
                  <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Abordagens</h3>
                    <div className="flex flex-wrap gap-2">
                      {psychologist.approaches.map(approach => (
                        <span
                          key={approach.id}
                          className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm"
                        >
                          {approach.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {psychologist.rating > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                      <Star className="mr-2 text-yellow-400 fill-yellow-400" size={20} />
                      Avaliação
                    </h3>
                    <p className="text-gray-700">
                      {psychologist.rating.toFixed(1)} ({psychologist.total_reviews} avaliações)
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Patient View */}
        {!user.is_psychologist && (
          <div className="card p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Bem-vindo à Lumine!
            </h2>
            <p className="text-gray-600 mb-6">
              Use nossa busca para encontrar psicólogos que atendam suas necessidades.
            </p>
            <div className="flex gap-4 justify-center">
              <a href="/buscar" className="btn-primary inline-flex items-center">
                Buscar Psicólogos
              </a>
              <a href="/dashboard/cliente" className="btn-secondary inline-flex items-center">
                Meu Dashboard
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

