import { useState, useEffect, useRef } from 'react'
import { 
  Send, 
  Download, 
  Trash2, 
  Copy,
  CheckCircle,
  AlertCircle,
  Clock,
  User,
  Bot
} from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'
import { chatApi, apiUtils } from '../api/client'

const ChatInterface = ({ instance }) => {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    loadChatHistory()
  }, [instance.id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    adjustTextareaHeight()
  }, [newMessage])

  const loadChatHistory = async () => {
    try {
      const response = await chatApi.getHistory(instance.id, 50)
      setMessages(response.data.messages || [])
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || sending) return

    const messageText = newMessage.trim()
    setNewMessage('')
    setSending(true)

    try {
      const response = await chatApi.sendMessage({
        instance_id: instance.id,
        message: messageText,
        stream: false
      })

      // Reload chat history to get the latest messages
      await loadChatHistory()
      
      if (response.data.error) {
        toast.error(`Error: ${response.data.error}`)
      }
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
      return
    }

    try {
      await chatApi.clearHistory(instance.id)
      setMessages([])
      toast.success('Chat history cleared')
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleExportHistory = async (format = 'json') => {
    try {
      const response = await chatApi.exportHistory(instance.id, format)
      
      // Create download link
      const blob = new Blob([response.data], { 
        type: format === 'json' ? 'application/json' : 'text/plain' 
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `chat_history_${instance.name}_${format === 'json' ? 'json' : 'txt'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.success('Chat history exported')
    } catch (error) {
      toast.error(apiUtils.formatError(error))
    }
  }

  const handleCopyMessage = async (content) => {
    try {
      await navigator.clipboard.writeText(content)
      toast.success('Message copied to clipboard')
    } catch (error) {
      toast.error('Failed to copy message')
    }
  }

  const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user'
    const isError = message.status === 'error'
    
    const MessageIcon = isUser ? User : Bot
    const StatusIcon = message.status === 'delivered' ? CheckCircle : 
                      message.status === 'error' ? AlertCircle : Clock

    return (
      <div className={clsx(
        'chat-message',
        isUser ? 'user' : 'assistant'
      )}>
        <div className={clsx(
          'flex flex-col max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl',
          isUser ? 'items-end' : 'items-start'
        )}>
          {/* Message header */}
          <div className={clsx(
            'flex items-center space-x-2 mb-1 text-xs text-gray-500',
            isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'
          )}>
            <MessageIcon className="h-3 w-3" />
            <span>{isUser ? 'You' : instance.name}</span>
            <span>{format(new Date(message.timestamp), 'HH:mm')}</span>
            <StatusIcon className={clsx(
              'h-3 w-3',
              message.status === 'delivered' ? 'text-green-500' : 
              message.status === 'error' ? 'text-red-500' : 'text-yellow-500'
            )} />
          </div>

          {/* Message bubble */}
          <div className={clsx(
            'chat-bubble group relative',
            isUser ? 'user' : 'assistant',
            isError && 'border border-red-300'
          )}>
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
            
            {/* Copy button */}
            <button
              onClick={() => handleCopyMessage(message.content)}
              className={clsx(
                'absolute top-2 opacity-0 group-hover:opacity-100 transition-opacity',
                'p-1 rounded hover:bg-black hover:bg-opacity-10',
                isUser ? 'left-2' : 'right-2'
              )}
              title="Copy message"
            >
              <Copy className="h-3 w-3" />
            </button>

            {/* Error indicator */}
            {isError && message.metadata?.error && (
              <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                Error: {message.metadata.error}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner h-8 w-8 mx-auto mb-4" />
          <p className="text-gray-600">Loading chat history...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Chat with {instance.name}
          </h3>
          <p className="text-sm text-gray-600">
            {messages.length} message{messages.length !== 1 ? 's' : ''}
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => handleExportHistory('json')}
            className="btn btn-outline btn-sm"
            title="Export as JSON"
          >
            <Download className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleExportHistory('txt')}
            className="btn btn-outline btn-sm"
            title="Export as Text"
          >
            <Download className="h-4 w-4" />
          </button>
          <button
            onClick={handleClearHistory}
            className="btn btn-danger btn-sm"
            title="Clear History"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No messages yet
            </h3>
            <p className="text-gray-600">
              Start a conversation with {instance.name} by sending a message below.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {sending && (
              <div className="chat-message assistant">
                <div className="flex items-center space-x-2 text-gray-500">
                  <Bot className="h-4 w-4" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm">Claude is thinking...</span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="flex space-x-3">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${instance.name}...`}
              className="w-full min-h-[44px] max-h-32 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-claude-500 focus:border-claude-500"
              disabled={sending}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!newMessage.trim() || sending}
            className={clsx(
              'btn btn-primary touch-target',
              (!newMessage.trim() || sending) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {sending ? (
              <div className="loading-spinner" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface