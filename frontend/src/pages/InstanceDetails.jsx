import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Settings, 
  Trash2, 
  ExternalLink,
  RefreshCw,
  Play,
  Square,
  Container,
  Monitor
} from 'lucide-react'
import toast from 'react-hot-toast'
import { instancesApi, dockerApi, apiUtils } from '../api/client'
import ChatInterface from '../components/ChatInterface'
import StatusIndicator from '../components/StatusIndicator'
import InstanceForm from '../components/InstanceForm'

const InstanceDetails = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [instance, setInstance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showEditForm, setShowEditForm] = useState(false)
  const [formLoading, setFormLoading] = useState(false)

  useEffect(() => {
    loadInstance()
  }, [id])

  const loadInstance = async () => {
    try {
      const response = await instancesApi.get(id)
      setInstance(response.data)
    } catch (error) {
      toast.error(apiUtils.formatError(error))
      if (error.response?.status === 404) {
        navigate('/')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleHealthCheck = async () => {
    try {
      await instancesApi.checkHealth(id)
      toast.success('Health check completed')
      await loadInstance()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleEditInstance = async (data) => {
    setFormLoading(true)
    try {
      await instancesApi.update(id, data)
      toast.success('Instance updated successfully')
      setShowEditForm(false)
      await loadInstance()
    } catch (error) {
      throw new Error(apiUtils.formatError(error))
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteInstance = async () => {
    if (!confirm(`Are you sure you want to delete "${instance.name}"? This action cannot be undone.`)) {
      return
    }

    try {
      await instancesApi.delete(id)
      toast.success('Instance deleted successfully')
      navigate('/')
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleStartContainer = async () => {
    if (!instance.container_id) return
    
    try {
      await dockerApi.startContainer(instance.container_id)
      toast.success('Container started successfully')
      await loadInstance()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleStopContainer = async () => {
    if (!instance.container_id) return
    
    try {
      await dockerApi.stopContainer(instance.container_id)
      toast.success('Container stopped successfully')
      await loadInstance()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">Loading instance...</p>
        </div>
      </div>
    )
  }

  if (!instance) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Instance not found</h2>
          <p className="text-gray-600 mb-4">The requested instance could not be found.</p>
          <Link to="/" className="btn btn-primary">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const TypeIcon = instance.type === 'docker' ? Container : Monitor

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link 
                to="/" 
                className="mr-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </Link>
              <div className="flex items-center space-x-3">
                <TypeIcon className="h-6 w-6 text-gray-400" />
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    {instance.name}
                  </h1>
                  <p className="text-sm text-gray-600">
                    {instance.host}:{instance.port}
                  </p>
                </div>
                <StatusIndicator status={instance.status} />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleHealthCheck}
                className="btn btn-outline btn-sm"
                title="Health Check"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
              
              {instance.url && (
                <a
                  href={instance.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline btn-sm"
                  title="Open Direct"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
              
              {instance.type === 'docker' && instance.container_id && (
                <>
                  <button
                    onClick={handleStartContainer}
                    className="btn btn-success btn-sm"
                    title="Start Container"
                  >
                    <Play className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleStopContainer}
                    className="btn btn-secondary btn-sm"
                    title="Stop Container"
                  >
                    <Square className="h-4 w-4" />
                  </button>
                </>
              )}
              
              <button
                onClick={() => setShowEditForm(true)}
                className="btn btn-outline btn-sm"
                title="Edit Instance"
              >
                <Settings className="h-4 w-4" />
              </button>
              
              <button
                onClick={handleDeleteInstance}
                className="btn btn-danger btn-sm"
                title="Delete Instance"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Instance Info Panel (Mobile) */}
      <div className="lg:hidden bg-white border-b border-gray-200 p-4">
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Type:</span>
              <span className="ml-2 capitalize">{instance.type}</span>
            </div>
            <div>
              <span className="text-gray-600">Status:</span>
              <span className="ml-2">
                <StatusIndicator status={instance.status} size="xs" />
              </span>
            </div>
          </div>
          
          {instance.last_seen && (
            <div className="text-sm">
              <span className="text-gray-600">Last Seen:</span>
              <span className="ml-2">
                {new Date(instance.last_seen).toLocaleDateString()} {new Date(instance.last_seen).toLocaleTimeString()}
              </span>
            </div>
          )}
          
          {instance.type === 'docker' && instance.metadata && (
            <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
              {instance.metadata.container_name && (
                <div>Container: {instance.metadata.container_name}</div>
              )}
              {instance.metadata.image && (
                <div>Image: {instance.metadata.image}</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar (Desktop) */}
        <aside className="hidden lg:block w-80 bg-white border-r border-gray-200">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Instance Details
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <StatusIndicator status={instance.status} />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <div className="flex items-center space-x-2">
                  <TypeIcon className="h-4 w-4 text-gray-400" />
                  <span className="capitalize">{instance.type}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Connection
                </label>
                <div className="text-sm text-gray-900 font-mono">
                  {instance.host}:{instance.port}
                </div>
                {instance.url && (
                  <a
                    href={instance.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-claude-600 hover:text-claude-700"
                  >
                    {instance.url}
                  </a>
                )}
              </div>
              
              {instance.last_seen && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Seen
                  </label>
                  <div className="text-sm text-gray-900">
                    {new Date(instance.last_seen).toLocaleDateString()}
                  </div>
                  <div className="text-sm text-gray-600">
                    {new Date(instance.last_seen).toLocaleTimeString()}
                  </div>
                </div>
              )}
              
              {instance.type === 'docker' && instance.metadata && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Docker Info
                  </label>
                  <div className="text-sm space-y-1">
                    {instance.metadata.container_name && (
                      <div>
                        <span className="text-gray-600">Container:</span>
                        <span className="ml-2 font-mono">{instance.metadata.container_name}</span>
                      </div>
                    )}
                    {instance.metadata.image && (
                      <div>
                        <span className="text-gray-600">Image:</span>
                        <span className="ml-2 font-mono">{instance.metadata.image}</span>
                      </div>
                    )}
                    {instance.container_id && (
                      <div>
                        <span className="text-gray-600">ID:</span>
                        <span className="ml-2 font-mono text-xs">{instance.container_id.substring(0, 12)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* Chat Interface */}
        <main className="flex-1 flex flex-col">
          <ChatInterface instance={instance} />
        </main>
      </div>

      {/* Edit Form Modal */}
      {showEditForm && (
        <InstanceForm
          instance={instance}
          onSave={handleEditInstance}
          onCancel={() => setShowEditForm(false)}
          isLoading={formLoading}
        />
      )}
    </div>
  )
}

export default InstanceDetails