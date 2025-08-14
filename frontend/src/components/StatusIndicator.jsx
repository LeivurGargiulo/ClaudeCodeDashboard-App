import { Circle, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react'
import { clsx } from 'clsx'

const StatusIndicator = ({ status, className, showText = true, size = 'sm' }) => {
  const statusConfig = {
    online: {
      icon: CheckCircle,
      text: 'Online',
      className: 'text-green-600 bg-green-100',
      iconColor: 'text-green-600'
    },
    offline: {
      icon: XCircle,
      text: 'Offline',
      className: 'text-red-600 bg-red-100',
      iconColor: 'text-red-600'
    },
    error: {
      icon: AlertCircle,
      text: 'Error',
      className: 'text-yellow-600 bg-yellow-100',
      iconColor: 'text-yellow-600'
    },
    unknown: {
      icon: Clock,
      text: 'Unknown',
      className: 'text-gray-600 bg-gray-100',
      iconColor: 'text-gray-600'
    }
  }

  const config = statusConfig[status] || statusConfig.unknown
  const Icon = config.icon

  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  }

  const textSizeClasses = {
    xs: 'text-xs',
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  }

  if (showText) {
    return (
      <span className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full font-medium',
        config.className,
        textSizeClasses[size],
        className
      )}>
        <Icon className={clsx(sizeClasses[size], 'mr-1.5')} />
        {config.text}
      </span>
    )
  }

  return (
    <Icon 
      className={clsx(
        sizeClasses[size],
        config.iconColor,
        className
      )}
      title={config.text}
    />
  )
}

export default StatusIndicator