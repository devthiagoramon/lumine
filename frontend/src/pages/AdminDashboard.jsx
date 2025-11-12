import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Shield, Users, MessageSquare, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import PsychologistManagement from '../components/admin/PsychologistManagement'
import ForumManagement from '../components/admin/ForumManagement'

const AdminDashboard = () => {
  const { user, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('psychologists')

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login')
    } else if (user && !user.is_admin) {
      navigate('/dashboard')
    }
  }, [user, authLoading, navigate])

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="card p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!user || !user.is_admin) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="text-primary-600" size={32} />
            <h1 className="text-4xl font-bold text-gray-900">
              Painel Administrativo
            </h1>
          </div>
          <p className="text-gray-600">
            Gerencie psicólogos e fóruns da plataforma
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('psychologists')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'psychologists'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Users size={20} />
                <span>Validação de Psicólogos</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('forum')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'forum'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <MessageSquare size={20} />
                <span>Gerenciamento de Fóruns</span>
              </div>
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="card p-6">
          {activeTab === 'psychologists' && <PsychologistManagement />}
          {activeTab === 'forum' && <ForumManagement />}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard

