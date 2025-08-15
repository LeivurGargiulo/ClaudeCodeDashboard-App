import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  RefreshCw, 
  Search, 
  Settings, 
  Container,
  Monitor,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'
import { instancesApi, dockerApi, apiUtils } from '../api/client'
import InstanceCard from '../components/InstanceCard'
import InstanceForm from '../components/InstanceForm'
import StatusIndicator from '../components/StatusIndicator'

const Dashboard = () => {
  const [instances, setInstances] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showInstanceForm, setShowInstanceForm] = useState(false)
  const [editingInstance, setEditingInstance] = useState(null)
  const [formLoading, setFormLoading] = useState(false)

  // Load data on component mount
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [instancesRes, statsRes] = await Promise.all([
        instancesApi.getAll(),
        instancesApi.getStats()
      ])
      
      setInstances(instancesRes.data)
      setStats(statsRes.data)
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await Promise.all([
        loadData(),
        instancesApi.checkAllHealth()
      ])
      toast.success('Refreshed successfully')
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setRefreshing(false)
    }
  }

  const handleDiscoverDocker = async () => {
    try {
      const response = await instancesApi.discoverDocker()
      const { discovered_count } = response.data
      
      if (discovered_count > 0) {
        toast.success(`Discovered ${discovered_count} Docker instance(s)`)
        await loadData()
      } else {
        toast('No new Docker instances found', { icon: 'ℹ️' })
      }
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleCreateInstance = async (data) => {
    setFormLoading(true)
    try {
      await instancesApi.create(data)
      toast.success('Instance created successfully')
      setShowInstanceForm(false)
      await loadData()
    } catch (error) {
      throw new Error(apiUtils.formatError(error))
    } finally {
      setFormLoading(false)
    }
  }

  const handleEditInstance = async (data) => {
    setFormLoading(true)
    try {
      await instancesApi.update(editingInstance.id, data)
      toast.success('Instance updated successfully')
      setEditingInstance(null)
      await loadData()
    } catch (error) {
      throw new Error(apiUtils.formatError(error))
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteInstance = async (instanceId) => {
    if (!confirm('Are you sure you want to delete this instance?')) {
      return
    }

    try {
      await instancesApi.delete(instanceId)
      toast.success('Instance deleted successfully')
      await loadData()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleHealthCheck = async (instanceId) => {
    try {
      await instancesApi.checkHealth(instanceId)
      toast.success('Health check completed')
      await loadData()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleStartContainer = async (containerId) => {
    try {
      await dockerApi.startContainer(containerId)
      toast.success('Container started successfully')
      await loadData()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleStopContainer = async (containerId) => {
    try {
      await dockerApi.stopContainer(containerId)
      toast.success('Container stopped successfully')
      await loadData()
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  // Filter instances based on search term
  const filteredInstances = instances.filter(instance =>
    instance.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    instance.host.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">Loading instances...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                Claude Code Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="btn btn-outline btn-sm"
                title="Refresh"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              </button>
              <Link to="/analytics" className="btn btn-outline btn-sm" title="Analytics">
                <BarChart3 className="h-4 w-4" />
              </Link>
              <Link to="/settings" className="btn btn-outline btn-sm" title="Settings">
                <Settings className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="card">
              <div className="card-body text-center">
                <Monitor className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                <div className="text-sm text-gray-600">Total Instances</div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-green-600">{stats.online}</div>
                <div className="text-sm text-gray-600">Online</div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <XCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-red-600">{stats.offline}</div>
                <div className="text-sm text-gray-600">Offline</div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <Container className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-600">{stats.docker}</div>
                <div className="text-sm text-gray-600">Docker</div>
              </div>
            </div>
          </div>
        )}

        {/* Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-4 sm:space-y-0">
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search instances..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleDiscoverDocker}
              className="btn btn-secondary btn-sm"
            >
              <Container className="h-4 w-4 mr-2" />
              Discover Docker
            </button>
            <button
              onClick={() => setShowInstanceForm(true)}
              className="btn btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Instance
            </button>
          </div>
        </div>

        {/* Instances Grid */}
        {filteredInstances.length === 0 ? (
          <div className="text-center py-12">
            <Monitor className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {instances.length === 0 ? 'No instances yet' : 'No instances match your search'}
            </h3>
            <p className="text-gray-600 mb-6">
              {instances.length === 0 
                ? 'Get started by adding your first Claude Code instance or discovering Docker containers.'
                : 'Try adjusting your search terms or add a new instance.'
              }
            </p>
            <div className="flex flex-col sm:flex-row justify-center space-y-2 sm:space-y-0 sm:space-x-4">
              <button
                onClick={() => setShowInstanceForm(true)}
                className="btn btn-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Instance
              </button>
              {instances.length === 0 && (
                <button
                  onClick={handleDiscoverDocker}
                  className="btn btn-secondary"
                >
                  <Container className="h-4 w-4 mr-2" />
                  Discover Docker
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="grid-responsive">
            {filteredInstances.map((instance) => (
              <InstanceCard
                key={instance.id}
                instance={instance}
                onEdit={setEditingInstance}
                onDelete={handleDeleteInstance}
                onHealthCheck={handleHealthCheck}
                onStart={handleStartContainer}
                onStop={handleStopContainer}
              />
            ))}
          </div>
        )}
      </main>

      {/* Instance Form Modal */}
      {showInstanceForm && (
        <InstanceForm
          onSave={handleCreateInstance}
          onCancel={() => setShowInstanceForm(false)}
          isLoading={formLoading}
        />
      )}

      {/* Edit Instance Form Modal */}
      {editingInstance && (
        <InstanceForm
          instance={editingInstance}
          onSave={handleEditInstance}
          onCancel={() => setEditingInstance(null)}
          isLoading={formLoading}
        />
      )}
    </div>
  )
}

export default Dashboard