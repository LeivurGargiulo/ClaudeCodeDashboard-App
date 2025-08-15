import React, { useState } from 'react'
import { 
  BarChart3, 
  DollarSign, 
  Zap,
  Activity,
  Eye,
  EyeOff
} from 'lucide-react'

const UsageChart = ({ data }) => {
  const [selectedMetric, setSelectedMetric] = useState('cost')
  const [showModels, setShowModels] = useState(false)

  if (!data || !data.timeline) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No usage data available</p>
        </div>
      </div>
    )
  }

  const timeline = data.timeline || []
  
  // Calculate max values for scaling
  const maxCost = Math.max(...timeline.map(t => t.total_cost || 0))
  const maxTokens = Math.max(...timeline.map(t => t.total_tokens || 0))
  const maxRequests = Math.max(...timeline.map(t => t.requests || 0))

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(amount)
  }

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num)
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: data.summary?.group_by === 'hour' ? 'numeric' : undefined
    })
  }

  const getBarHeight = (value, max) => {
    if (!max || max === 0) return 0
    return Math.max((value / max) * 100, 1) // Minimum 1% for visibility
  }

  const getMetricValue = (period) => {
    switch (selectedMetric) {
      case 'cost':
        return period.total_cost || 0
      case 'tokens':
        return period.total_tokens || 0
      case 'requests':
        return period.requests || 0
      default:
        return 0
    }
  }

  const getMetricMax = () => {
    switch (selectedMetric) {
      case 'cost':
        return maxCost
      case 'tokens':
        return maxTokens
      case 'requests':
        return maxRequests
      default:
        return 1
    }
  }

  const formatMetricValue = (value) => {
    switch (selectedMetric) {
      case 'cost':
        return formatCurrency(value)
      case 'tokens':
        return formatNumber(value)
      case 'requests':
        return formatNumber(value)
      default:
        return value
    }
  }

  const metricConfig = {
    cost: {
      icon: DollarSign,
      label: 'Cost',
      color: 'green',
      bgClass: 'bg-green-500',
      lightBgClass: 'bg-green-100',
      textClass: 'text-green-700'
    },
    tokens: {
      icon: Zap,
      label: 'Tokens',
      color: 'blue',
      bgClass: 'bg-blue-500',
      lightBgClass: 'bg-blue-100',
      textClass: 'text-blue-700'
    },
    requests: {
      icon: Activity,
      label: 'Requests',
      color: 'purple',
      bgClass: 'bg-purple-500',
      lightBgClass: 'bg-purple-100',
      textClass: 'text-purple-700'
    }
  }

  const currentConfig = metricConfig[selectedMetric]

  // Get model colors
  const modelColors = {
    'claude-3-opus': '#ef4444',      // red
    'claude-3.5-sonnet': '#3b82f6',  // blue
    'claude-3-sonnet': '#6366f1',    // indigo
    'claude-3-haiku': '#10b981',     // emerald
    'unknown': '#6b7280'             // gray
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {Object.entries(metricConfig).map(([key, config]) => {
            const Icon = config.icon
            return (
              <button
                key={key}
                onClick={() => setSelectedMetric(key)}
                className={`flex items-center space-x-1 px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  selectedMetric === key
                    ? `${config.bgClass} text-white`
                    : `${config.lightBgClass} ${config.textClass} hover:${config.bgClass} hover:text-white`
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{config.label}</span>
              </button>
            )
          })}
        </div>
        
        <button
          onClick={() => setShowModels(!showModels)}
          className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
        >
          {showModels ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          <span>{showModels ? 'Hide' : 'Show'} Models</span>
        </button>
      </div>

      {/* Chart */}
      <div className="relative">
        <div className="flex items-end space-x-1 h-64 bg-gray-50 rounded-lg p-4 overflow-x-auto">
          {timeline.map((period, index) => (
            <div
              key={index}
              className="flex-shrink-0 flex flex-col items-center group relative"
              style={{ minWidth: '40px' }}
            >
              {/* Bar */}
              <div className="relative flex flex-col items-center h-full justify-end">
                {showModels && period.models ? (
                  // Stacked bars by model
                  <div className="flex flex-col justify-end h-full w-8">
                    {Object.entries(period.models).map(([model, modelData]) => {
                      const modelValue = selectedMetric === 'cost' ? modelData.cost : 
                                       selectedMetric === 'tokens' ? modelData.tokens : 
                                       modelData.requests
                      const height = getBarHeight(modelValue, getMetricMax())
                      
                      return (
                        <div
                          key={model}
                          className="w-full transition-all duration-200 hover:opacity-80"
                          style={{
                            height: `${height}%`,
                            backgroundColor: modelColors[model] || modelColors.unknown
                          }}
                          title={`${model}: ${formatMetricValue(modelValue)}`}
                        />
                      )
                    })}
                  </div>
                ) : (
                  // Single bar
                  <div
                    className={`w-8 ${currentConfig.bgClass} transition-all duration-200 hover:opacity-80 rounded-t-sm`}
                    style={{
                      height: `${getBarHeight(getMetricValue(period), getMetricMax())}%`
                    }}
                  />
                )}
                
                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
                  <div className="font-medium">{formatDate(period.period)}</div>
                  <div>{formatMetricValue(getMetricValue(period))}</div>
                  {showModels && period.models && (
                    <div className="mt-1 pt-1 border-t border-gray-700">
                      {Object.entries(period.models).map(([model, modelData]) => {
                        const modelValue = selectedMetric === 'cost' ? modelData.cost : 
                                         selectedMetric === 'tokens' ? modelData.tokens : 
                                         modelData.requests
                        return (
                          <div key={model} className="flex justify-between space-x-2">
                            <span className="text-gray-300">{model.replace('claude-', '')}:</span>
                            <span>{formatMetricValue(modelValue)}</span>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>
              
              {/* Date label */}
              <div className="mt-2 text-xs text-gray-600 transform -rotate-45 origin-left">
                {formatDate(period.period)}
              </div>
            </div>
          ))}
        </div>

        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 h-64 flex flex-col justify-between py-4 pr-2">
          <span className="text-xs text-gray-500">{formatMetricValue(getMetricMax())}</span>
          <span className="text-xs text-gray-500">{formatMetricValue(getMetricMax() * 0.75)}</span>
          <span className="text-xs text-gray-500">{formatMetricValue(getMetricMax() * 0.5)}</span>
          <span className="text-xs text-gray-500">{formatMetricValue(getMetricMax() * 0.25)}</span>
          <span className="text-xs text-gray-500">0</span>
        </div>
      </div>

      {/* Legend */}
      {showModels && (
        <div className="flex flex-wrap gap-2 text-xs">
          {Object.entries(modelColors).map(([model, color]) => (
            <div key={model} className="flex items-center space-x-1">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: color }}
              />
              <span className="text-gray-600">{model.replace('claude-', '')}</span>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {data.summary && (
        <div className="flex items-center justify-between text-sm text-gray-500 pt-2 border-t border-gray-200">
          <span>
            Showing {timeline.length} {data.summary.group_by}ly periods
          </span>
          <span>
            {new Date(data.summary.date_range.start).toLocaleDateString()} - 
            {new Date(data.summary.date_range.end).toLocaleDateString()}
          </span>
        </div>
      )}
    </div>
  )
}

export default UsageChart