import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  ArrowLeft, 
  Save, 
  RefreshCw,
  Container,
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react'
import toast from 'react-hot-toast'
import { healthApi, dockerApi, instancesApi, apiUtils } from '../api/client'

const Settings = () => {
  const [dockerStatus, setDockerStatus] = useState(null)
  const [appHealth, setAppHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const [healthRes, dockerRes, statsRes] = await Promise.all([
        healthApi.getInfo(),
        dockerApi.getStatus().catch(() => ({ data: { available: false, status: 'error' } })),
        instancesApi.getStats().catch(() => ({ data: null }))
      ])
      
      setAppHealth(healthRes.data)
      setDockerStatus(dockerRes.data)
      setStats(statsRes.data)
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setLoading(true)
    await loadSettings()
  }

  const handleTestConnection = async () => {
    try {
      const response = await healthApi.check()
      if (response.status === 200) {
        toast.success('Backend connection successful')
      }
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleDiscoverDocker = async () => {
    try {
      const response = await instancesApi.discoverDocker()
      const { discovered_count } = response.data
      
      if (discovered_count > 0) {
        toast.success(`Discovered ${discovered_count} Docker instance(s)`)
      } else {
        toast('No new Docker instances found', { icon: 'ℹ️' })
      }
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleReconnectDocker = async () => {
    try {
      const response = await dockerApi.reconnect()
      const { success, message } = response.data
      
      if (success) {
        toast.success(message)
        await loadSettings() // Reload to update status
      } else {
        toast.error(message)
      }
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link 
                to="/" 
                className="mr-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            </div>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="btn btn-outline btn-sm"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Application Status */}
          <section className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">Application Status</h2>
            </div>
            <div className="card-body space-y-4">
              {appHealth && (
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{appHealth.name}</h3>
                    <p className="text-sm text-gray-600">Version {appHealth.version}</p>
                    <p className="text-sm text-gray-600">{appHealth.description}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              )}
              
              <div className="flex justify-end">
                <button
                  onClick={handleTestConnection}
                  className="btn btn-outline btn-sm"
                >
                  Test Connection
                </button>
              </div>
            </div>
          </section>

          {/* Instance Statistics */}
          {stats && (
            <section className="card">
              <div className="card-header">
                <h2 className="text-lg font-semibold text-gray-900">Instance Statistics</h2>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                    <div className="text-sm text-gray-600">Total Instances</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{stats.online}</div>
                    <div className="text-sm text-gray-600">Online</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{stats.offline}</div>
                    <div className="text-sm text-gray-600">Offline</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{stats.docker}</div>
                    <div className="text-sm text-gray-600">Docker</div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Docker Integration */}
          <section className="card">
            <div className="card-header">
              <div className="flex items-center space-x-2">
                <Container className="h-5 w-5 text-gray-400" />
                <h2 className="text-lg font-semibold text-gray-900">Docker Integration</h2>
              </div>
            </div>
            <div className="card-body space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">Docker Status</h3>
                  <p className="text-sm text-gray-600">
                    Docker daemon connection status
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {dockerStatus?.available ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="text-sm text-green-600 capitalize">
                        {dockerStatus.status}
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <span className="text-sm text-red-600">
                        Not Available
                      </span>
                    </>
                  )}
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                {dockerStatus?.available ? (
                  <button
                    onClick={handleDiscoverDocker}
                    className="btn btn-primary btn-sm"
                  >
                    <Container className="h-4 w-4 mr-2" />
                    Discover Instances
                  </button>
                ) : (
                  <button
                    onClick={handleReconnectDocker}
                    className="btn btn-secondary btn-sm"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reconnect Docker
                  </button>
                )}
              </div>

              {!dockerStatus?.available && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                  <div className="flex">
                    <AlertCircle className="h-5 w-5 text-yellow-400 mt-0.5 mr-2 flex-shrink-0" />
                    <div className="text-sm text-yellow-700">
                      <p className="font-medium mb-1">Docker not available</p>
                      <p>
                        Make sure Docker Desktop is running, then click "Reconnect Docker" above.
                        On Windows, Docker Desktop must be started and the engine must be running.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Network Configuration */}
          <section className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">Network Configuration</h2>
            </div>
            <div className="card-body space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <Info className="h-5 w-5 text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
                  <div className="text-sm text-blue-700">
                    <p className="font-medium mb-1">Remote Access via Tailscale</p>
                    <p>
                      This dashboard is configured to be accessible remotely via Tailscale. 
                      The backend binds to 0.0.0.0 and can be accessed from any device 
                      connected to your Tailscale network.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">
                    Frontend URL
                  </label>
                  <div className="font-mono text-gray-900 bg-gray-50 p-2 rounded">
                    {window.location.origin}
                  </div>
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">
                    Backend API URL
                  </label>
                  <div className="font-mono text-gray-900 bg-gray-50 p-2 rounded">
                    {window.location.origin}/api
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* About */}
          <section className="card">
            <div className="card-header">
              <h2 className="text-lg font-semibold text-gray-900">About</h2>
            </div>
            <div className="card-body">
              <div className="text-sm text-gray-600 space-y-2">
                <p>
                  Claude Code Dashboard is a web application for managing and interacting 
                  with multiple Claude Code instances, both local and containerized.
                </p>
                <p>
                  Features include instance management, real-time chat interfaces, 
                  Docker container discovery, and mobile-friendly responsive design.
                </p>
                <p>
                  Built with FastAPI (backend) and React (frontend) for modern, 
                  fast, and reliable operation.
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

export default Settings