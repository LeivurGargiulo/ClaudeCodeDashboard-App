import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  MoreVertical, 
  MessageCircle, 
  Settings, 
  Trash2, 
  Play, 
  Square,
  ExternalLink,
  Container,
  Monitor,
  Clock
} from 'lucide-react'
import { format } from 'date-fns'
import { clsx } from 'clsx'
import StatusIndicator from './StatusIndicator'

const InstanceCard = ({ 
  instance, 
  onEdit, 
  onDelete, 
  onHealthCheck,
  onStart,
  onStop
}) => {
  const [showMenu, setShowMenu] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleHealthCheck = async () => {
    if (isLoading) return
    setIsLoading(true)
    try {
      await onHealthCheck(instance.id)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAction = async (action) => {
    if (isLoading) return
    setIsLoading(true)
    setShowMenu(false)
    try {
      await action()
    } finally {
      setIsLoading(false)
    }
  }

  const TypeIcon = instance.type === 'docker' ? Container : Monitor

  return (
    <div className={clsx(
      'card hover:shadow-md transition-shadow duration-200',
      isLoading && 'opacity-75 pointer-events-none'
    )}>
      <div className="card-body">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <TypeIcon className="h-5 w-5 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {instance.name}
            </h3>
          </div>
          
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 rounded-full hover:bg-gray-100 transition-colors"
              disabled={isLoading}
            >
              <MoreVertical className="h-4 w-4 text-gray-500" />
            </button>
            
            {showMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-10">
                <Link
                  to={`/instance/${instance.id}`}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowMenu(false)}
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Open Chat
                </Link>
                
                <button
                  onClick={() => handleAction(() => onEdit(instance))}
                  className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Edit
                </button>
                
                {instance.url && (
                  <a
                    href={instance.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setShowMenu(false)}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open Direct
                  </a>
                )}
                
                {instance.type === 'docker' && instance.container_id && (
                  <>
                    <div className="border-t border-gray-100 my-1"></div>
                    <button
                      onClick={() => handleAction(() => onStart(instance.container_id))}
                      className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Start Container
                    </button>
                    <button
                      onClick={() => handleAction(() => onStop(instance.container_id))}
                      className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <Square className="h-4 w-4 mr-2" />
                      Stop Container
                    </button>
                  </>
                )}
                
                <div className="border-t border-gray-100 my-1"></div>
                <button
                  onClick={() => handleAction(() => onDelete(instance.id))}
                  className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Status */}
        <div className="mb-3">
          <StatusIndicator status={instance.status} />
        </div>

        {/* Connection Info */}
        <div className="space-y-2 mb-4 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Host:</span>
            <span className="font-mono">{instance.host}:{instance.port}</span>
          </div>
          
          <div className="flex justify-between">
            <span>Type:</span>
            <span className="capitalize">{instance.type}</span>
          </div>
          
          {instance.last_seen && (
            <div className="flex justify-between">
              <span>Last Seen:</span>
              <span title={instance.last_seen}>
                {format(new Date(instance.last_seen), 'MMM d, HH:mm')}
              </span>
            </div>
          )}
        </div>

        {/* Container Info for Docker instances */}
        {instance.type === 'docker' && instance.metadata && (
          <div className="text-xs text-gray-500 mb-4 p-2 bg-gray-50 rounded">
            {instance.metadata.container_name && (
              <div>Container: {instance.metadata.container_name}</div>
            )}
            {instance.metadata.image && (
              <div>Image: {instance.metadata.image}</div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2">
          <Link
            to={`/instance/${instance.id}`}
            className="btn btn-primary btn-sm flex-1 mobile-button"
          >
            <MessageCircle className="h-4 w-4 mr-1" />
            Chat
          </Link>
          
          <button
            onClick={handleHealthCheck}
            disabled={isLoading}
            className={clsx(
              'btn btn-outline btn-sm touch-target',
              isLoading && 'opacity-50 cursor-not-allowed'
            )}
            title="Check Health"
          >
            {isLoading ? (
              <div className="loading-spinner" />
            ) : (
              <Clock className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default InstanceCard