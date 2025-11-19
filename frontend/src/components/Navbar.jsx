import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Search, User, LogOut, Menu, X, Shield, DollarSign, Wallet } from 'lucide-react'
import { useState } from 'react'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">L</span>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
              Lumine
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              to="/buscar"
              className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors"
            >
              <Search size={18} />
              <span>Buscar Psicólogos</span>
            </Link>
            <Link
              to="/forum"
              className="text-gray-700 hover:text-primary-600 transition-colors"
            >
              Fórum
            </Link>
            {user && !user.is_psychologist && (
              <>
                <Link
                  to="/diario"
                  className="text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Diário
                </Link>
                <Link
                  to="/pagamentos"
                  className="text-gray-700 hover:text-primary-600 transition-colors flex items-center gap-1"
                >
                  <DollarSign size={18} />
                  <span>Pagamentos</span>
                </Link>
              </>
            )}
            {user && user.is_psychologist && (
              <Link
                to="/historico-financeiro"
                className="text-gray-700 hover:text-primary-600 transition-colors flex items-center gap-1"
              >
                <Wallet size={18} />
                <span>Financeiro</span>
              </Link>
            )}
            {user && user.is_admin && (
              <Link
                to="/admin"
                className="text-gray-700 hover:text-primary-600 transition-colors flex items-center gap-1"
              >
                <Shield size={18} />
                <span>Admin</span>
              </Link>
            )}

            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors"
                >
                  <User size={18} />
                  <span>{user.full_name}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-700 hover:text-red-600 transition-colors"
                >
                  <LogOut size={18} />
                  <span>Sair</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Entrar
                </Link>
                <Link
                  to="/cadastro"
                  className="btn-primary"
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 space-y-3">
            <Link
              to="/buscar"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              onClick={() => setMobileMenuOpen(false)}
            >
              Buscar Psicólogos
            </Link>
            <Link
              to="/forum"
              className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              onClick={() => setMobileMenuOpen(false)}
            >
              Fórum
            </Link>
            {user && !user.is_psychologist && (
              <>
                <Link
                  to="/diario"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Diário
                </Link>
                <Link
                  to="/pagamentos"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Pagamentos
                </Link>
              </>
            )}
            {user && user.is_psychologist && (
              <Link
                to="/historico-financeiro"
                className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Histórico Financeiro
              </Link>
            )}
            {user && user.is_admin && (
              <Link
                to="/admin"
                className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Painel Admin
              </Link>
            )}
            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Meu Perfil
                </Link>
                <button
                  onClick={() => {
                    handleLogout()
                    setMobileMenuOpen(false)
                  }}
                  className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Sair
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Entrar
                </Link>
                <Link
                  to="/cadastro"
                  className="block px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar

