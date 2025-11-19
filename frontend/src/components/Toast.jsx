import { useEffect } from 'react'
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react'

const Toast = ({ message, type = 'info', onClose, duration = 5000 }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info
  }

  const styles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  }

  const iconColors = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600'
  }

  const Icon = icons[type] || Info

  return (
    <div
      className={`min-w-[300px] max-w-md p-4 rounded-lg shadow-lg border-2 flex items-start gap-3 animate-slide-in-right ${styles[type]}`}
      role="alert"
    >
      <Icon className={`flex-shrink-0 mt-0.5 ${iconColors[type]}`} size={20} />
      <div className="flex-1">
        <p className="font-medium text-sm">{message}</p>
      </div>
      <button
        onClick={onClose}
        className={`flex-shrink-0 ml-2 ${iconColors[type]} hover:opacity-70 transition-opacity`}
        aria-label="Fechar notificação"
      >
        <X size={18} />
      </button>
    </div>
  )
}

export default Toast

