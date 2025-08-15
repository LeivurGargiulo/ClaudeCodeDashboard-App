import React from 'react'
import { AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'

const UsageStatsBar = ({ stats }) => {
  if (!stats) return null

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num)
  }

  // Calculate usage percentages
  const costUsagePercent = stats.cost_quota ? (stats.current_cost / stats.cost_quota * 100) : 0
  const tokenUsagePercent = stats.token_quota ? (stats.current_tokens / stats.token_quota * 100) : 0
  const requestUsagePercent = stats.request_quota ? (stats.current_requests / stats.request_quota * 100) : 0

  // Determine status colors
  const getStatusColor = (percentage) => {
    if (percentage >= 90) return 'red'
    if (percentage >= 75) return 'yellow'
    return 'green'
  }

  const getStatusIcon = (percentage) => {
    if (percentage >= 90) return AlertTriangle
    if (percentage >= 75) return TrendingUp
    return CheckCircle
  }

  const ProgressBar = ({ 
    label, 
    current, 
    quota, 
    percentage, 
    formatValue = (v) => v, 
    showQuota = true 
  }) => {
    const color = getStatusColor(percentage)
    const Icon = getStatusIcon(percentage)
    
    const colorClasses = {
      green: {
        bg: 'bg-green-500',
        text: 'text-green-700',
        icon: 'text-green-600',
        lightBg: 'bg-green-50'
      },
      yellow: {
        bg: 'bg-yellow-500',
        text: 'text-yellow-700',
        icon: 'text-yellow-600',
        lightBg: 'bg-yellow-50'
      },
      red: {
        bg: 'bg-red-500',
        text: 'text-red-700',
        icon: 'text-red-600',
        lightBg: 'bg-red-50'
      }
    }

    return (
      <div className={`rounded-lg p-4 ${colorClasses[color].lightBg} border border-${color}-200`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Icon className={`h-5 w-5 ${colorClasses[color].icon}`} />
            <span className="font-medium text-gray-900">{label}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <span className={`font-semibold ${colorClasses[color].text}`}>
              {formatValue(current)}
            </span>
            {showQuota && quota && (
              <>
                <span className="text-gray-500">/</span>
                <span className="text-gray-700">{formatValue(quota)}</span>
              </>
            )}
          </div>
        </div>
        
        {quota ? (
          <>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full transition-all duration-300 ${colorClasses[color].bg}`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
            <div className="flex justify-between items-center mt-1">
              <span className="text-xs text-gray-500">
                {percentage.toFixed(1)}% used
              </span>
              {percentage > 100 && (
                <span className="text-xs text-red-600 font-medium">
                  Over quota by {(percentage - 100).toFixed(1)}%
                </span>
              )}
            </div>
          </>
        ) : (
          <div className="mt-1">
            <span className="text-xs text-gray-500">No quota set</span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Current Usage Summary
        </h2>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <span>
            Period: {new Date(stats.current_period_start).toLocaleDateString()} - 
            {new Date(stats.current_period_end).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Cost Usage */}
        <ProgressBar
          label="Cost"
          current={stats.current_cost}
          quota={stats.cost_quota}
          percentage={costUsagePercent}
          formatValue={formatCurrency}
        />

        {/* Token Usage */}
        <ProgressBar
          label="Tokens"
          current={stats.current_tokens}
          quota={stats.token_quota}
          percentage={tokenUsagePercent}
          formatValue={formatNumber}
        />

        {/* Request Usage */}
        <ProgressBar
          label="Requests"
          current={stats.current_requests}
          quota={stats.request_quota}
          percentage={requestUsagePercent}
          formatValue={formatNumber}
        />
      </div>

      {/* Additional Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Projected Monthly Cost:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatCurrency(stats.projected_monthly_cost)}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Daily Average:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatCurrency(stats.daily_average_cost)}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Trend:</span>
            <span className={`ml-2 font-medium capitalize ${
              stats.trend_direction === 'increasing' ? 'text-red-600' :
              stats.trend_direction === 'decreasing' ? 'text-green-600' :
              'text-gray-600'
            }`}>
              {stats.trend_direction}
            </span>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {(costUsagePercent > 80 || tokenUsagePercent > 80 || requestUsagePercent > 80) && (
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-amber-800">Usage Warning</p>
              <p className="text-amber-700">
                You're approaching your usage quotas. Consider monitoring your usage more closely 
                or adjusting your quotas to avoid service interruptions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UsageStatsBar