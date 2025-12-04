import { useEffect, useRef } from 'react'
import { Bot } from 'lucide-react'
import { Message } from './Message'
import { Loading } from '../ui/Loading'
import { Logo } from '../common/Logo'
import { cn } from '../../utils/cn'

/**
 * Contenedor principal del chat
 * @param {Object} props
 * @param {Array} props.messages - Array de mensajes
 * @param {boolean} props.isLoading - Si está cargando
 */
export function ChatContainer({ messages, isLoading }) {
  const messagesEndRef = useRef(null)
  const containerRef = useRef(null)

  // Auto-scroll al último mensaje
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isLoading])

  return (
    <div
      ref={containerRef}
      className={cn(
        'flex-1 overflow-y-auto overflow-x-hidden',
        'scrollbar-thin scrollbar-thumb-dark-border-primary scrollbar-track-dark-bg-primary',
        messages.length === 0 && 'flex items-center justify-center'
      )}
    >
      {messages.length === 0 ? (
        <div className="w-full px-4 py-32">
          <div className="text-center max-w-2xl mx-auto">
            <div className="flex justify-center mb-6">
              <Logo size="lg" />
            </div>
            <h2 className="text-2xl font-medium text-dark-text-primary mb-3 tracking-tight">
              Bienvenido a NetMind
            </h2>
            <p className="text-dark-text-secondary text-[15px] leading-relaxed max-w-lg mx-auto">
              Asistente inteligente especializado en redes y telecomunicaciones.
              Soporte técnico en conceptos de red, consultas DNS, análisis de direcciones IP y gestión de documentación técnica.
            </p>
            <div className="mt-8 flex flex-wrap gap-2 justify-center">
              <span className="px-4 py-2 bg-dark-surface-primary border border-dark-border-primary/30 rounded-full text-sm text-dark-text-secondary">
                Consultas DNS
              </span>
              <span className="px-4 py-2 bg-dark-surface-primary border border-dark-border-primary/30 rounded-full text-sm text-dark-text-secondary">
                Operaciones de Red
              </span>
              <span className="px-4 py-2 bg-dark-surface-primary border border-dark-border-primary/30 rounded-full text-sm text-dark-text-secondary">
                Documentación RAG
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="py-4 sm:py-6 overflow-x-hidden">
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="flex gap-3 px-4 py-3 animate-fade-in">
              <div className="flex-shrink-0">
                <Logo size="sm" />
              </div>
              <div className="bg-dark-surface-primary border border-dark-border-primary/50 rounded-2xl px-4 py-3 shadow-gemini-sm">
                <Loading size="sm" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  )
}

