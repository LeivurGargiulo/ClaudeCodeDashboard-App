import React, { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  DollarSign, 
  Zap, 
  Download,
  Calendar,
  Filter,
  RefreshCw,
  Clock,
  Users,
  Activity
} from 'lucide-react'
import { usageApi, instancesApi } from '../api/client'
import { apiUtils } from '../api/client'
import toast from 'react-hot-toast'
import UsageChart from '../components/UsageChart'
import ModelBreakdown from '../components/ModelBreakdown'
import UsageStatsBar from '../components/UsageStatsBar'

const Analytics = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [modelBreakdown, setModelBreakdown] = useState(null)
  const [instances, setInstances] = useState([])
  
  // Filters
  const [selectedInstance, setSelectedInstance] = useState('')
  const [timeRange, setTimeRange] = useState(30) // days
  const [groupBy, setGroupBy] = useState('day')
  
  // Export
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    loadData()
  }, [selectedInstance, timeRange, groupBy])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load all data in parallel
      const [statsRes, timelineRes, modelsRes, instancesRes] = await Promise.all([
        usageApi.getStats(),
        usageApi.getTimeline({ 
          days: timeRange, 
          instance_id: selectedInstance || undefined,
          group_by: groupBy 
        }),
        usageApi.getModelBreakdown({ 
          days: timeRange, 
          instance_id: selectedInstance || undefined 
        }),
        instancesApi.getAll()
      ])
      
      setStats(statsRes.data)
      setTimeline(timelineRes.data)
      setModelBreakdown(modelsRes.data)
      setInstances(instancesRes.data)
      
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    try {
      setExporting(true)
      
      const exportRequest = {
        format: format,
        query: {
          start_date: new Date(Date.now() - timeRange * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date().toISOString(),
          instance_id: selectedInstance || null,
          limit: 10000
        },
        include_raw_data: true,
        include_aggregations: true
      }
      
      const response = await usageApi.exportData(exportRequest)
      toast.success(`Export completed: ${response.data.message}`)
      
      // Trigger download
      if (response.data.download_url) {
        window.open(response.data.download_url, '_blank')
      }
      
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setExporting(false)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-lg">Loading analytics...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Usage Analytics
        </h1>
        <p className="text-gray-600">
          Comprehensive token usage and cost analysis for your Claude Code instances
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Instance Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={selectedInstance}
              onChange={(e) => setSelectedInstance(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Instances</option>
              {instances.map(instance => (
                <option key={instance.id} value={instance.id}>
                  {instance.name}
                </option>
              ))}
            </select>
          </div>

          {/* Time Range */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>

          {/* Group By */}
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4 text-gray-500" />
            <select
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="hour">Hourly</option>
              <option value="day">Daily</option>
              <option value="week">Weekly</option>
            </select>
          </div>

          {/* Refresh */}
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          {/* Export */}
          <div className="flex items-center space-x-2 ml-auto">
            <span className="text-sm text-gray-500">Export:</span>
            <button
              onClick={() => handleExport('json')}
              disabled={exporting}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50"
            >
              JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              disabled={exporting}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50"
            >
              CSV
            </button>
          </div>
        </div>
      </div>

      {/* Usage Stats Bar */}
      {stats && (
        <div className="mb-6">
          <UsageStatsBar stats={stats} />
        </div>
      )}

      {/* Key Metrics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DollarSign className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Current Period Cost
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(stats.current_cost)}
                    </div>
                    <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                      <span className="text-xs text-gray-500">
                        / {formatCurrency(stats.cost_quota || 0)} quota
                      </span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Zap className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Tokens Used
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {formatNumber(stats.current_tokens)}
                    </div>
                    <div className="ml-2 flex items-baseline text-sm font-semibold text-blue-600">
                      <TrendingUp className="h-4 w-4" />
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Activity className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Requests
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {formatNumber(stats.current_requests)}
                    </div>
                    <div className="ml-2 flex items-baseline text-sm text-gray-500">
                      <span className="text-xs">this period</span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Projected Monthly
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {formatCurrency(stats.projected_monthly_cost)}
                    </div>
                    <div className="ml-2 flex items-baseline text-sm text-gray-500">
                      <span className={`text-xs px-1 py-0.5 rounded ${
                        stats.trend_direction === 'increasing' ? 'bg-red-100 text-red-600' :
                        stats.trend_direction === 'decreasing' ? 'bg-green-100 text-green-600' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {stats.trend_direction}
                      </span>
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Usage Timeline Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Usage Timeline
          </h3>
          {timeline && <UsageChart data={timeline} />}
        </div>

        {/* Model Breakdown */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Usage by Model
          </h3>
          {modelBreakdown && <ModelBreakdown data={modelBreakdown} />}
        </div>
      </div>

      {/* Additional Insights */}
      {stats && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Usage Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Daily Averages</h4>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Cost:</span>
                  <span className="text-sm font-medium">{formatCurrency(stats.daily_average_cost)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Tokens:</span>
                  <span className="text-sm font-medium">{formatNumber(stats.daily_average_tokens)}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Current Period</h4>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Start:</span>
                  <span className="text-sm font-medium">
                    {new Date(stats.current_period_start).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">End:</span>
                  <span className="text-sm font-medium">
                    {new Date(stats.current_period_end).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Quota Usage</h4>
              <div className="space-y-1">
                {stats.cost_quota && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Cost:</span>
                    <span className="text-sm font-medium">{stats.cost_usage_percent.toFixed(1)}%</span>
                  </div>
                )}
                {stats.token_quota && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Tokens:</span>
                    <span className="text-sm font-medium">{stats.token_usage_percent.toFixed(1)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Analytics