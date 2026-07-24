import { useState, useRef } from 'react'
import { transcribeAudio } from '@/api/endpoints'

/**
 * VoiceInput — Zia STT mic button (Step 4.1b).
 *
 * Records audio via MediaRecorder, sends to /api/voice/transcribe (Zia Services),
 * and calls onTranscription(text) with the result.
 *
 * Falls back to a disabled state with a tooltip when Zia STT endpoint is not live.
 *
 * Props:
 *   language        — 'EN' | 'KN'
 *   onTranscription — (text: string) => void
 *   disabled        — force disabled (e.g. while AI is responding)
 */
export default function VoiceInput({ language, onTranscription, disabled }) {
  const [recording, setRecording] = useState(false)
  const [error, setError] = useState(null)
  const mediaRef = useRef(null)
  const chunksRef = useRef([])

  async function startRecording() {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)
      mediaRef.current = mr
      chunksRef.current = []

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        try {
          const result = await transcribeAudio(blob, language)
          if (!result.text) {
            throw new Error(result.message || 'Zia STT is not configured')
          }
          onTranscription?.(result.text)
        } catch (err) {
          setError(err.message || 'Zia STT unavailable — type your query instead')
        }
      }

      mr.start()
      setRecording(true)
    } catch (err) {
      setError('Microphone access denied')
      console.warn('[VoiceInput]', err)
    }
  }

  function stopRecording() {
    mediaRef.current?.stop()
    setRecording(false)
  }

  return (
    <div className="relative">
      <button
        type="button"
        disabled={disabled}
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`relative px-3 py-2 rounded-sm border transition-colors ${
          recording
            ? 'border-alert text-alert bg-alert/10 animate-pulse'
            : 'border-border text-ink-dim hover:text-gold-bright hover:border-gold'
        } disabled:opacity-40 disabled:cursor-not-allowed`}
        title={`Hold to record in ${language === 'KN' ? 'Kannada' : 'English'} (Zia STT)`}
        aria-label="Hold to record voice input"
      >
        {recording ? '⏺' : '🎙'}
      </button>
      {error && (
        <div className="absolute bottom-full left-0 mb-1 text-[10px] font-mono text-alert bg-navy-900 border border-alert/30 px-2 py-1 rounded-sm whitespace-nowrap z-10">
          {error}
        </div>
      )}
    </div>
  )
}
