import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Save, AlertCircle } from 'lucide-react'
import { clsx } from 'clsx'

// Validation schema
const instanceSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  host: z.string().min(1, 'Host is required').max(255, 'Host must be less than 255 characters'),
  port: z.coerce.number().min(1, 'Port must be greater than 0').max(65535, 'Port must be less than 65536'),
  type: z.enum(['local', 'docker']),
  container_id: z.string().optional(),
})

const InstanceForm = ({ 
  instance = null, 
  onSave, 
  onCancel, 
  isLoading = false 
}) => {
  const [submitError, setSubmitError] = useState('')
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
    reset
  } = useForm({
    resolver: zodResolver(instanceSchema),
    defaultValues: {
      name: instance?.name || '',
      host: instance?.host || 'localhost',
      port: instance?.port || 8000,
      type: instance?.type || 'local',
      container_id: instance?.container_id || '',
    }
  })

  const watchType = watch('type')

  useEffect(() => {
    if (instance) {
      reset({
        name: instance.name,
        host: instance.host,
        port: instance.port,
        type: instance.type,
        container_id: instance.container_id || '',
      })
    }
  }, [instance, reset])

  const onSubmit = async (data) => {
    setSubmitError('')
    try {
      // Clean up data before sending
      const payload = {
        ...data,
        container_id: data.container_id || undefined,
      }
      
      await onSave(payload)
    } catch (error) {
      setSubmitError(error.message || 'Failed to save instance')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {instance ? 'Edit Instance' : 'Add New Instance'}
          </h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            disabled={isLoading}
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
          {/* Name */}
          <div>
            <label className="form-label">
              Instance Name *
            </label>
            <input
              {...register('name')}
              type="text"
              className={clsx(
                'form-input',
                errors.name && 'border-red-500 focus:border-red-500 focus:ring-red-500'
              )}
              placeholder="My Claude Instance"
              disabled={isLoading}
            />
            {errors.name && (
              <p className="form-error">{errors.name.message}</p>
            )}
          </div>

          {/* Type */}
          <div>
            <label className="form-label">
              Instance Type
            </label>
            <select
              {...register('type')}
              className="form-input"
              disabled={isLoading || !!instance} // Don't allow type change for existing instances
            >
              <option value="local">Local Instance</option>
              <option value="docker">Docker Container</option>
            </select>
            {errors.type && (
              <p className="form-error">{errors.type.message}</p>
            )}
          </div>

          {/* Host */}
          <div>
            <label className="form-label">
              Host *
            </label>
            <input
              {...register('host')}
              type="text"
              className={clsx(
                'form-input',
                errors.host && 'border-red-500 focus:border-red-500 focus:ring-red-500'
              )}
              placeholder="localhost"
              disabled={isLoading}
            />
            {errors.host && (
              <p className="form-error">{errors.host.message}</p>
            )}
          </div>

          {/* Port */}
          <div>
            <label className="form-label">
              Port *
            </label>
            <input
              {...register('port')}
              type="number"
              className={clsx(
                'form-input',
                errors.port && 'border-red-500 focus:border-red-500 focus:ring-red-500'
              )}
              placeholder="8000"
              min="1"
              max="65535"
              disabled={isLoading}
            />
            {errors.port && (
              <p className="form-error">{errors.port.message}</p>
            )}
          </div>

          {/* Container ID (only for Docker instances) */}
          {watchType === 'docker' && (
            <div>
              <label className="form-label">
                Container ID (optional)
              </label>
              <input
                {...register('container_id')}
                type="text"
                className="form-input"
                placeholder="container_id_or_name"
                disabled={isLoading}
              />
              <p className="mt-1 text-sm text-gray-500">
                Leave empty to auto-detect during discovery
              </p>
            </div>
          )}

          {/* Common ports hint */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">Common Claude Code ports:</p>
                <p>8000 (default), 8080, 3000, 5000</p>
              </div>
            </div>
          </div>

          {/* Submit Error */}
          {submitError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 mr-2 flex-shrink-0" />
                <p className="text-sm text-red-700">{submitError}</p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-outline mobile-button"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={clsx(
                'btn btn-primary mobile-button',
                (!isValid || isLoading) && 'opacity-50 cursor-not-allowed'
              )}
              disabled={!isValid || isLoading}
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {instance ? 'Update' : 'Create'} Instance
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InstanceForm