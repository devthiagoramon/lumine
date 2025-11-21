import { BarChart3 } from 'lucide-react'

const EmotionChart = ({ data, title = "Frequência de Emoções" }) => {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <BarChart3 className="mx-auto mb-2 text-gray-400" size={32} />
        <p>Nenhum dado para exibir</p>
      </div>
    )
  }

  const maxCount = Math.max(...data.map(item => item.count), 1)

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      <div className="space-y-3">
        {data.map((item, index) => {
          const percentage = (item.count / maxCount) * 100
          return (
            <div key={index} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700 capitalize">
                  {item.emotion}
                </span>
                <span className="text-gray-600">
                  {item.count} {item.count === 1 ? 'vez' : 'vezes'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
                <div
                  className="bg-blue-600 h-6 rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${percentage}%` }}
                >
                  {percentage > 10 && (
                    <span className="text-xs text-white font-medium">
                      {item.count}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default EmotionChart



