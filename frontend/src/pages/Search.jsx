import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { Search as SearchIcon, MapPin, Star, Filter, X } from 'lucide-react'
import PsychologistCard from '../components/PsychologistCard'

const Search = () => {
  const [psychologists, setPsychologists] = useState([])
  const [loading, setLoading] = useState(true)
  const [hasSearched, setHasSearched] = useState(false)
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
  
  // Ref para rastrear se é a primeira montagem
  const isInitialMount = useRef(true)
  // Refs para manter os valores atuais sem causar re-renderizações
  const filtersRef = useRef(filters)
  const pageRef = useRef(page)
  
  // Atualizar refs quando os valores mudarem
  useEffect(() => {
    filtersRef.current = filters
  }, [filters])
  
  useEffect(() => {
    pageRef.current = page
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

  // Memoizar a função de busca para evitar recriações desnecessárias
  // A função recebe os valores como parâmetros, então não precisa de dependências
  const searchPsychologists = useCallback(async (currentPage, currentFilters) => {
    setLoading(true)
    try {
      // Mapear parâmetros do inglês para português (como o backend espera)
      const params = {
        pagina: currentPage,
        tamanho_pagina: 12
      }

      // Mapear filtros
      if (currentFilters.query) params.consulta = currentFilters.query
      if (currentFilters.city) params.cidade = currentFilters.city
      if (currentFilters.state) params.estado = currentFilters.state
      if (currentFilters.specialty_ids && currentFilters.specialty_ids.length > 0) {
        params.ids_especialidades = currentFilters.specialty_ids
      }
      if (currentFilters.approach_ids && currentFilters.approach_ids.length > 0) {
        params.ids_abordagens = currentFilters.approach_ids
      }
      if (currentFilters.online_consultation !== null) {
        params.consulta_online = currentFilters.online_consultation
      }
      if (currentFilters.in_person_consultation !== null) {
        params.consulta_presencial = currentFilters.in_person_consultation
      }
      if (currentFilters.min_rating !== null) {
        params.avaliacao_minima = currentFilters.min_rating
      }
      if (currentFilters.max_price !== null) {
        params.preco_maximo = currentFilters.max_price
      }

      console.log('🔍 Buscando psicólogos com parâmetros:', params)
      const response = await axios.get('/api/search/psychologists', { params })
      console.log('✅ Resposta da API:', response.data)
      console.log('📊 Psicólogos recebidos:', response.data?.psychologists)
      console.log('📈 Total:', response.data?.total)
      
      // Só atualizar o estado se a resposta for válida
      if (response.data) {
        const psychologistsList = response.data.psychologists || []
        const totalCount = response.data.total || 0
        
        console.log('💾 Atualizando estado com:', {
          psychologists: psychologistsList.length,
          total: totalCount
        })
        
        setPsychologists(psychologistsList)
        setTotal(totalCount)
        setHasSearched(true)
        
        console.log('✅ Estado atualizado com sucesso')
      } else {
        console.warn('⚠️ Resposta da API não contém dados válidos')
        setPsychologists([])
        setTotal(0)
        setHasSearched(true)
      }
    } catch (error) {
      console.error('❌ Erro ao buscar psicólogos:', error)
      console.error('📋 Detalhes do erro:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      // Só limpar o estado se já tiver feito uma busca anterior
      if (hasSearched) {
        setPsychologists([])
        setTotal(0)
      }
      // Marcar que a busca foi tentada, mesmo em caso de erro
      setHasSearched(true)
    } finally {
      setLoading(false)
    }
  }, [])

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
    searchPsychologists(1, filters)
  }

  const clearFilters = () => {
    const emptyFilters = {
      query: '',
      city: '',
      state: '',
      specialty_ids: [],
      approach_ids: [],
      online_consultation: null,
      in_person_consultation: null,
      min_rating: null,
      max_price: null,
    }
    setFilters(emptyFilters)
    setPage(1)
    // Buscar imediatamente após limpar filtros
    searchPsychologists(1, emptyFilters)
  }

  // Carregar especialidades e abordagens na inicialização
  useEffect(() => {
    fetchSpecialtiesAndApproaches()
  }, [])

  // Buscar psicólogos na inicialização (apenas uma vez)
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false
      searchPsychologists(1, filtersRef.current)
    }
  }, [searchPsychologists])

  // Buscar psicólogos quando a página mudar (mas não na inicialização)
  useEffect(() => {
    if (!isInitialMount.current) {
      searchPsychologists(pageRef.current, filtersRef.current)
    }
  }, [page, searchPsychologists])

  // Buscar psicólogos quando os filtros mudarem (com debounce)
  useEffect(() => {
    // Ignorar a primeira renderização
    if (isInitialMount.current) {
      return
    }

    const timer = setTimeout(() => {
      // Resetar para página 1 quando os filtros mudarem
      // O useEffect de [page] vai buscar automaticamente quando a página mudar
      if (pageRef.current !== 1) {
        setPage(1)
      } else {
        // Se já estiver na página 1, buscar diretamente
        searchPsychologists(1, filtersRef.current)
      }
    }, 500)
    
    return () => clearTimeout(timer)
  }, [filters, searchPsychologists])

  // Debug: Monitorar mudanças no estado
  useEffect(() => {
    console.log('📊 Estado atualizado:', {
      psychologists: psychologists.length,
      total,
      loading,
      hasSearched
    })
  }, [psychologists, total, loading, hasSearched])

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
        ) : !loading && hasSearched && psychologists.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg mb-4">
              Nenhum psicólogo encontrado com os filtros selecionados.
            </p>
            <button onClick={clearFilters} className="btn-primary">
              Limpar Filtros
            </button>
          </div>
        ) : !loading && psychologists.length > 0 ? (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {psychologists.map((psychologist, index) => {
                console.log(`🔄 Renderizando psicólogo ${index + 1}:`, psychologist)
                // Verificar se os dados necessários estão presentes
                if (!psychologist || !psychologist.user) {
                  console.warn(`⚠️ Psicólogo ${index + 1} sem dados completos:`, psychologist)
                  // Fallback: card simples com dados básicos
                  return (
                    <div key={psychologist?.id || index} className="card p-6">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {psychologist?.user?.nome_completo || 'Psicólogo'}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">CRP: {psychologist?.crp || 'N/A'}</p>
                      {psychologist?.specialties && psychologist.specialties.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {psychologist.specialties.slice(0, 3).map(spec => (
                            <span key={spec.id} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                              {spec.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )
                }
                return (
                  <PsychologistCard key={psychologist.id || index} psychologist={psychologist} />
                )
              })}
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
        ) : null}
      </div>
    </div>
  )
}

export default Search

