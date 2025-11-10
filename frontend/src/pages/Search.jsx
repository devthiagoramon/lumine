import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { Search as SearchIcon, MapPin, Star, Filter, X } from 'lucide-react'
import PsychologistCard from '../components/PsychologistCard'

const Search = () => {
  const [psychologists, setPsychologists] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [filters, setFilters] = useState({
    query: '',
    city: '',
    state: '',
    specialty_ids: [],
    approach_ids: [],
    online_consultation: null,
    in_person_consultation: null,
    min_rating: null,
    max_price: null,
  })
  const [specialties, setSpecialties] = useState([])
  const [approaches, setApproaches] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  useEffect(() => {
    fetchSpecialtiesAndApproaches()
    searchPsychologists()
  }, [page])

  const fetchSpecialtiesAndApproaches = async () => {
    try {
      const [specRes, appRes] = await Promise.all([
        axios.get('/api/search/specialties'),
        axios.get('/api/search/approaches')
      ])
      setSpecialties(specRes.data)
      setApproaches(appRes.data)
    } catch (error) {
      console.error('Erro ao carregar filtros:', error)
    }
  }

  const searchPsychologists = async () => {
    setLoading(true)
    try {
      const params = {
        page,
        page_size: 12,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => 
            v !== null && v !== '' && (Array.isArray(v) ? v.length > 0 : true)
          )
        )
      }

      // Converter arrays para query params
      if (filters.specialty_ids.length > 0) {
        params.specialty_ids = filters.specialty_ids
      }
      if (filters.approach_ids.length > 0) {
        params.approach_ids = filters.approach_ids
      }

      const response = await axios.get('/api/search/psychologists', { params })
      setPsychologists(response.data.psychologists)
      setTotal(response.data.total)
    } catch (error) {
      console.error('Erro ao buscar psicólogos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleToggleFilter = (key, value) => {
    setFilters(prev => {
      const current = prev[key]
      if (Array.isArray(current)) {
        const index = current.indexOf(value)
        if (index > -1) {
          return { ...prev, [key]: current.filter(v => v !== value) }
        } else {
          return { ...prev, [key]: [...current, value] }
        }
      }
      return { ...prev, [key]: value }
    })
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    searchPsychologists()
  }

  const clearFilters = () => {
    setFilters({
      query: '',
      city: '',
      state: '',
      specialty_ids: [],
      approach_ids: [],
      online_consultation: null,
      in_person_consultation: null,
      min_rating: null,
      max_price: null,
    })
    setPage(1)
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      if (page === 1) {
        searchPsychologists()
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [filters])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Buscar Psicólogos
          </h1>
          <p className="text-gray-600">
            Encontre o profissional ideal para você
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar por nome, especialidade ou CRP..."
                value={filters.query}
                onChange={(e) => handleFilterChange('query', e.target.value)}
                className="input-field pl-12"
              />
            </div>
            <button
              type="button"
              onClick={() => setFiltersOpen(!filtersOpen)}
              className="btn-secondary flex items-center gap-2"
            >
              <Filter size={20} />
              Filtros
            </button>
            <button type="submit" className="btn-primary">
              Buscar
            </button>
          </div>
        </form>

        {/* Filters Panel */}
        {filtersOpen && (
          <div className="card p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-900">Filtros</h3>
              <button
                onClick={clearFilters}
                className="text-primary-600 hover:text-primary-700 text-sm"
              >
                Limpar todos
              </button>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Localização */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cidade
                </label>
                <input
                  type="text"
                  value={filters.city}
                  onChange={(e) => handleFilterChange('city', e.target.value)}
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
                  value={filters.state}
                  onChange={(e) => handleFilterChange('state', e.target.value)}
                  className="input-field"
                  placeholder="Ex: SP"
                />
              </div>

              {/* Tipo de Consulta */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Consulta
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.online_consultation === true}
                      onChange={(e) => handleFilterChange('online_consultation', e.target.checked ? true : null)}
                      className="mr-2"
                    />
                    <span>Online</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.in_person_consultation === true}
                      onChange={(e) => handleFilterChange('in_person_consultation', e.target.checked ? true : null)}
                      className="mr-2"
                    />
                    <span>Presencial</span>
                  </label>
                </div>
              </div>

              {/* Especialidades */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Especialidades
                </label>
                <div className="max-h-40 overflow-y-auto space-y-2">
                  {specialties.map(spec => (
                    <label key={spec.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.specialty_ids.includes(spec.id)}
                        onChange={() => handleToggleFilter('specialty_ids', spec.id)}
                        className="mr-2"
                      />
                      <span className="text-sm">{spec.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Abordagens */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Abordagens
                </label>
                <div className="max-h-40 overflow-y-auto space-y-2">
                  {approaches.map(approach => (
                    <label key={approach.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={filters.approach_ids.includes(approach.id)}
                        onChange={() => handleToggleFilter('approach_ids', approach.id)}
                        className="mr-2"
                      />
                      <span className="text-sm">{approach.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Rating e Preço */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Avaliação Mínima
                </label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={filters.min_rating || ''}
                  onChange={(e) => handleFilterChange('min_rating', e.target.value ? parseFloat(e.target.value) : null)}
                  className="input-field"
                  placeholder="Ex: 4.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preço Máximo (R$)
                </label>
                <input
                  type="number"
                  min="0"
                  value={filters.max_price || ''}
                  onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : null)}
                  className="input-field"
                  placeholder="Ex: 200"
                />
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        <div className="mb-4">
          <p className="text-gray-600">
            {loading ? 'Carregando...' : `${total} psicólogo(s) encontrado(s)`}
          </p>
        </div>

        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-48 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : psychologists.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg mb-4">
              Nenhum psicólogo encontrado com os filtros selecionados.
            </p>
            <button onClick={clearFilters} className="btn-primary">
              Limpar Filtros
            </button>
          </div>
        ) : (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {psychologists.map(psychologist => (
                <PsychologistCard key={psychologist.id} psychologist={psychologist} />
              ))}
            </div>

            {/* Pagination */}
            {total > 12 && (
              <div className="flex justify-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                <span className="flex items-center px-4">
                  Página {page} de {Math.ceil(total / 12)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= Math.ceil(total / 12)}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Próxima
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default Search

