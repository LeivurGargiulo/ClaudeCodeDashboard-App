import React from 'react'
import { PieChart, TrendingUp, Zap, DollarSign, Activity } from 'lucide-react'

const ModelBreakdown = ({ data }) => {
  if (!data || !data.model_breakdown) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <PieChart className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No model usage data available</p>
        </div>
      </div>
    )
  }

  const models = Object.entries(data.model_breakdown || {})
  const totalCost = data.summary?.total_cost || 0
  const totalTokens = data.summary?.total_tokens || 0

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

  // Model colors mapping
  const modelColors = {
    'claude-3-opus': '#ef4444',      // red
    'claude-3.5-sonnet': '#3b82f6',  // blue
    'claude-3-sonnet': '#6366f1',    // indigo
    'claude-3-haiku': '#10b981',     // emerald
    'unknown': '#6b7280'             // gray
  }

  const getModelColor = (modelName) => {
    return modelColors[modelName] || modelColors.unknown
  }

  const getDisplayName = (modelName) => {
    return modelName.replace('claude-', '').replace('-', ' ').toUpperCase()
  }

  // Sort models by cost (descending)
  const sortedModels = models.sort((a, b) => b[1].cost - a[1].cost)

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>{models.length} models used</span>
        <span>
          {data.summary?.date_range?.start && data.summary?.date_range?.end && (
            <>
              {new Date(data.summary.date_range.start).toLocaleDateString()} - 
              {new Date(data.summary.date_range.end).toLocaleDateString()}
            </>
          )}
        </span>
      </div>

      {/* Model List */}
      <div className="space-y-3">
        {sortedModels.map(([modelName, modelData]) => {
          const costPercentage = totalCost > 0 ? (modelData.cost / totalCost * 100) : 0
          const tokenPercentage = totalTokens > 0 ? (modelData.tokens / totalTokens * 100) : 0
          const color = getModelColor(modelName)

          return (
            <div key={modelName} className="bg-gray-50 rounded-lg p-4">
              {/* Model Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="font-medium text-gray-900">
                    {getDisplayName(modelName)}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="font-medium text-gray-900">
                    {formatCurrency(modelData.cost)}
                  </span>
                  <span className="text-gray-500">
                    ({costPercentage.toFixed(1)}%)
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div
                  className="h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${costPercentage}%`,
                    backgroundColor: color
                  }}
                />
              </div>

              {/* Model Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="flex items-center space-x-1">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <div>
                    <div className="text-gray-500">Cost</div>
                    <div className="font-medium">{formatCurrency(modelData.cost)}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <Zap className="h-4 w-4 text-blue-600" />
                  <div>
                    <div className="text-gray-500">Tokens</div>
                    <div className="font-medium">{formatNumber(modelData.tokens)}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <Activity className="h-4 w-4 text-purple-600" />
                  <div>
                    <div className="text-gray-500">Requests</div>
                    <div className="font-medium">{formatNumber(modelData.requests)}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-1">
                  <TrendingUp className="h-4 w-4 text-orange-600" />
                  <div>
                    <div className="text-gray-500">Avg/Request</div>
                    <div className="font-medium">{formatCurrency(modelData.avg_cost_per_request || 0)}</div>
                  </div>
                </div>
              </div>

              {/* Additional Metrics */}
              <div className="mt-3 pt-3 border-t border-gray-200 flex justify-between text-xs text-gray-500">
                <span>
                  Avg tokens/request: {formatNumber(modelData.avg_tokens_per_request || 0)}
                </span>
                <span>
                  Token share: {tokenPercentage.toFixed(1)}%
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Total Summary */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <PieChart className="h-5 w-5 text-blue-600" />
            <span className="font-medium text-blue-900">Total Usage</span>
          </div>
          <div className="text-right">
            <div className="text-lg font-semibold text-blue-900">
              {formatCurrency(totalCost)}
            </div>
            <div className="text-sm text-blue-700">
              {formatNumber(totalTokens)} tokens
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs">
        {sortedModels.map(([modelName]) => (
          <div key={modelName} className="flex items-center space-x-1">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: getModelColor(modelName) }}
            />
            <span className="text-gray-600">{getDisplayName(modelName)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ModelBreakdown