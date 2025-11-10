import { Link } from 'react-router-dom'
import { MapPin, Star, Monitor, Building2 } from 'lucide-react'

const PsychologistCard = ({ psychologist }) => {
  return (
    <Link to={`/psicologo/${psychologist.id}`}>
      <div className="card p-6 hover:shadow-xl transition-all duration-200 h-full flex flex-col">
        {/* Profile Picture */}
        <div className="flex items-center mb-4">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center text-white text-2xl font-bold mr-4">
            {psychologist.user.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900">
              {psychologist.user.full_name}
            </h3>
            <p className="text-sm text-gray-600">CRP: {psychologist.crp}</p>
          </div>
        </div>

        {/* Rating */}
        {psychologist.rating > 0 && (
          <div className="flex items-center mb-3">
            <Star className="text-yellow-400 fill-yellow-400" size={20} />
            <span className="ml-1 font-semibold text-gray-900">
              {psychologist.rating.toFixed(1)}
            </span>
            <span className="ml-1 text-gray-600 text-sm">
              ({psychologist.total_reviews} avaliações)
            </span>
          </div>
        )}

        {/* Bio */}
        {psychologist.bio && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-3 flex-1">
            {psychologist.bio}
          </p>
        )}

        {/* Specialties */}
        {psychologist.specialties.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {psychologist.specialties.slice(0, 3).map(spec => (
                <span
                  key={spec.id}
                  className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                >
                  {spec.name}
                </span>
              ))}
              {psychologist.specialties.length > 3 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                  +{psychologist.specialties.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Location and Consultation Types */}
        <div className="space-y-2 mt-auto">
          {psychologist.city && psychologist.state && (
            <div className="flex items-center text-gray-600 text-sm">
              <MapPin size={16} className="mr-1" />
              <span>
                {psychologist.city}, {psychologist.state}
              </span>
            </div>
          )}

          <div className="flex items-center gap-4 text-sm">
            {psychologist.online_consultation && (
              <div className="flex items-center text-gray-600">
                <Monitor size={16} className="mr-1" />
                <span>Online</span>
              </div>
            )}
            {psychologist.in_person_consultation && (
              <div className="flex items-center text-gray-600">
                <Building2 size={16} className="mr-1" />
                <span>Presencial</span>
              </div>
            )}
          </div>

          {psychologist.consultation_price && (
            <div className="text-lg font-bold text-primary-600">
              R$ {psychologist.consultation_price.toFixed(2)}
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}

export default PsychologistCard

