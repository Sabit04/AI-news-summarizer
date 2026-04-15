import { useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [mode, setMode] = useState('text') // 'text' | 'url'
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [maxLength, setMaxLength] = useState(150)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function handleSummarize(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const endpoint = mode === 'url' ? '/summarize-url' : '/summarize'
      const body =
        mode === 'url'
          ? { url, max_length: maxLength }
          : { text, max_length: maxLength }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || `Request failed (${res.status})`)
      }
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function handleFile(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      setText(String(reader.result || ''))
      setMode('text')
    }
    reader.readAsText(file)
  }

  const charCount = mode === 'text' ? text.length : url.length

  return (
    <div className="app">
      <header>
        <h1>AI News Summarizer</h1>
        <p className="sub">
          Transformer-based summarization · handles articles up to 20,000 characters
        </p>
      </header>

      <div className="tabs">
        <button
          className={mode === 'text' ? 'tab active' : 'tab'}
          onClick={() => setMode('text')}
        >
          Paste text
        </button>
        <button
          className={mode === 'url' ? 'tab active' : 'tab'}
          onClick={() => setMode('url')}
        >
          From URL
        </button>
      </div>

      <form onSubmit={handleSummarize}>
        {mode === 'text' ? (
          <>
            <textarea
              placeholder="Paste an article, essay, or any long-form text here (at least 50 characters)…"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              maxLength={20000}
            />
            <div className="row">
              <label className="file-upload">
                Upload .txt file
                <input type="file" accept=".txt,text/plain" onChange={handleFile} />
              </label>
              <span className="muted">{text.length.toLocaleString()} / 20,000 chars</span>
            </div>
          </>
        ) : (
          <input
            type="url"
            placeholder="https://example.com/article"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        )}

        <div className="row">
          <label className="length">
            Target length: <strong>{maxLength}</strong> tokens
            <input
              type="range"
              min="60"
              max="300"
              step="10"
              value={maxLength}
              onChange={(e) => setMaxLength(Number(e.target.value))}
            />
          </label>
          <button type="submit" className="primary" disabled={loading || charCount < 8}>
            {loading ? 'Summarizing…' : 'Summarize'}
          </button>
        </div>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="result">
          <h2>Summary</h2>
          <p className="summary">{result.summary}</p>
          <div className="meta">
            <span>Model: {result.model}</span>
            <span>Input: {result.input_chars?.toLocaleString()} chars</span>
            <span>{result.chunk_count} chunk{result.chunk_count === 1 ? '' : 's'}</span>
            {result.source_url && (
              <a href={result.source_url} target="_blank" rel="noreferrer">
                Source
              </a>
            )}
          </div>
        </section>
      )}

      <footer>
        <p className="muted small">
          Powered by Hugging Face · facebook/bart-large-cnn
        </p>
      </footer>
    </div>
  )
}
