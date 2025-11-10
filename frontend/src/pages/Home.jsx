import { Link } from 'react-router-dom'
import { Search, Heart, Shield, Users, ArrowRight, Star } from 'lucide-react'

const Home = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Encontre o psicólogo
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-secondary-600">
                ideal para você
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Conectamos você com profissionais de psicologia qualificados, 
              alinhados com suas necessidades e valores. Sua jornada de cuidado 
              mental começa aqui.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/buscar" className="btn-primary text-lg px-8 py-3 inline-flex items-center justify-center">
                <Search className="mr-2" size={20} />
                Buscar Psicólogos
              </Link>
              <Link to="/cadastro" className="btn-secondary text-lg px-8 py-3 inline-flex items-center justify-center">
                Começar Agora
                <ArrowRight className="ml-2" size={20} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Por que escolher a Lumine?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Facilitamos sua busca por um profissional de psicologia 
              que realmente se conecte com você
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card p-8 text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="text-primary-600" size={32} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Busca Inteligente
              </h3>
              <p className="text-gray-600">
                Filtre por especialidade, abordagem, localização e muito mais. 
                Encontre exatamente o que você precisa.
              </p>
            </div>

            <div className="card p-8 text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="text-secondary-600" size={32} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Compatibilidade
              </h3>
              <p className="text-gray-600">
                Conecte-se com profissionais que compartilham seus valores 
                e utilizam abordagens alinhadas às suas necessidades.
              </p>
            </div>

            <div className="card p-8 text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="text-primary-600" size={32} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Segurança e Confiança
              </h3>
              <p className="text-gray-600">
                Todos os profissionais são verificados e possuem registro 
                no CRP. Sua segurança é nossa prioridade.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Como funciona
            </h2>
            <p className="text-xl text-gray-600">
              Três passos simples para encontrar seu psicólogo ideal
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-bold">
                1
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Busque e Filtre
              </h3>
              <p className="text-gray-600">
                Use nossos filtros avançados para encontrar psicólogos 
                que atendam suas necessidades específicas.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-bold">
                2
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Conheça o Profissional
              </h3>
              <p className="text-gray-600">
                Leia perfis detalhados, especialidades, abordagens e 
                avaliações de outros pacientes.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-6 text-3xl font-bold">
                3
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                Entre em Contato
              </h3>
              <p className="text-gray-600">
                Entre em contato diretamente com o profissional e 
                inicie sua jornada de cuidado mental.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-secondary-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Pronto para começar sua jornada?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Encontre o psicólogo ideal para você hoje mesmo
          </p>
          <Link to="/buscar" className="bg-white text-primary-600 font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors inline-flex items-center">
            Buscar Agora
            <ArrowRight className="ml-2" size={20} />
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home

