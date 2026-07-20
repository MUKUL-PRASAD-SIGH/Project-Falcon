import { useState, useRef, useEffect, useCallback, useId } from 'react'
import CitationChip from './CitationChip'
import VoiceInput from './VoiceInput'
import ExportButton from './ExportButton'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'
import { postQuery } from '@/api/endpoints'
import { useRoleVoice } from '@/hooks/useRoleVoice'

const SESSION_ID = `session-${Date.now()}`

export default function ChatWindow() {
  const voice = useRoleVoice()

  // Seed messages are role-adaptive — Investigators see plain English, Analysts see technical language
  const [messages, setMessages] = useState(() => voice.seedMessages)
  const [input,    setInput]    = useState('')
  const [lang,     setLang]     = useState('EN')
  const [loading,  setLoading]  = useState(false)
  const bottomRef = useRef(null)
  const inputId   = useId()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const allCitations = messages
    .filter((m) => m.citations)
    .flatMap((m) => m.citations)

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || loading) return

    setMessages((prev) => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)

    try {
      const response = await postQuery(text, SESSION_ID, lang)
      setMessages((prev) => [
        ...prev,
        {
          role:      'ai',
          text:      response.answer ?? 'Response received.',
          citations: response.citations ?? [],
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role:      'ai',
          text:      'AI backend is not yet connected. This is demonstration mode.',
          citations: [],
        },
      ])
    } finally {
      setLoading(false)
    }
  }, [input, loading, lang])

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-8">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="flex items-start justify-between mb-5 gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-2xl font-bold">{voice.chatHeader}</h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-sm text-ink-dim">{voice.chatSubtitle}</p>
            {voice.chatTag && <span className="case-tag">{voice.chatTag}</span>}
          </div>
        </div>
        <ExportButton messages={messages} citations={allCitations} />
      </div>

      <div className="panel flex flex-col" style={{ height: '72vh' }}>

        {/* ── Message area ───────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto scroll-thin p-5 space-y-5">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {/* AI avatar */}
              {m.role === 'ai' && (
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-[10px] font-bold"
                  style={{
                    background:   'var(--role-accent-dim)',
                    color:        'var(--role-accent)',
                    border:       '1px solid var(--role-accent-glow)',
                  }}
                >
                  AI
                </div>
              )}

              {/* Bubble */}
              <div
                className={`max-w-[78%] px-4 py-3 text-sm leading-relaxed ${
                  m.role === 'user' ? 'rounded-2xl rounded-tr-sm' : 'rounded-2xl rounded-tl-sm'
                }`}
                style={
                  m.role === 'user'
                    ? { background: 'var(--role-accent-dim)', border: '1px solid var(--role-accent-glow)' }
                    : { background: 'rgba(10, 18, 36, 0.85)', border: '1px solid rgba(255,255,255,0.07)' }
                }
              >
                <p>{m.text}</p>
                {/* FIR citation chips — evidence trail */}
                {m.citations && m.citations.length > 0 && (
                  <div className="flex gap-1.5 mt-3 flex-wrap">
                    {m.citations.map((c) => (
                      <CitationChip key={c} firId={c} />
                    ))}
                  </div>
                )}
              </div>

              {/* User avatar */}
              {m.role === 'user' && (
                <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-[10px] font-bold bg-[rgba(255,255,255,0.07)] text-ink-dim border border-[rgba(255,255,255,0.1)]">
                  ME
                </div>
              )}
            </div>
          ))}

          {/* Loading bubble while Circuits pipeline processes */}
          {loading && (
            <div className="flex justify-start gap-3">
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[10px] font-bold"
                style={{ background: 'var(--role-accent-dim)', color: 'var(--role-accent)' }}
              >
                AI
              </div>
              <div
                className="max-w-[78%] w-64 rounded-2xl rounded-tl-sm px-4 py-3"
                style={{ background: 'rgba(10,18,36,0.85)', border: '1px solid rgba(255,255,255,0.07)' }}
              >
                <LoadingSkeleton className="h-4 w-full" lines={2} />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* ── Suggested prompt chips ─────────────────────────────── */}
        <div className="border-t border-[rgba(255,255,255,0.06)] px-3 py-2.5 flex gap-2 overflow-x-auto scroll-thin">
          {voice.suggestedPrompts.map((p) => (
            <button
              key={p}
              type="button"
              className="prompt-chip shrink-0"
              disabled={loading}
              onClick={() => setInput(p)}
            >
              {p}
            </button>
          ))}
        </div>

        {/* ── Input bar ──────────────────────────────────────────── */}
        <div className="border-t border-[rgba(255,255,255,0.06)] p-3 flex items-center gap-2">
          {/* Language toggle — Zia Services */}
          <button
            type="button"
            onClick={() => setLang((l) => (l === 'EN' ? 'KN' : 'EN'))}
            className="btn-ghost text-xs font-mono min-w-[36px] justify-center"
            title={lang === 'EN' ? 'Switch to Kannada (Zia Services)' : 'Switch to English'}
          >
            {lang}
          </button>

          {/* Zia STT microphone */}
          <VoiceInput
            language={lang}
            onTranscription={(text) => setInput(text)}
            disabled={loading}
          />

          {/* Query input */}
          <label htmlFor={inputId} className="sr-only">Query</label>
          <input
            id={inputId}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder={lang === 'KN' ? voice.chatPlaceholderKN : voice.chatPlaceholder}
          />

          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="btn-gold disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? '…' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}
