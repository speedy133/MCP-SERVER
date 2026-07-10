import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './index.css'

function App() {
  const [appName, setAppName] = useState('Groww')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!appName) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: appName
        })
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'Analysis failed')
      }

      setResult(data.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <header className="w-full max-w-container-max mx-auto px-gutter py-xl flex flex-col items-center text-center gap-md z-10 relative">
        <div className="flex flex-col items-center gap-sm">
          <img alt="Weekly Pulse Logo" className="w-16 h-16 rounded-lg shadow-[0_0_20px_rgba(208,188,255,0.3)] object-contain" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCyqyUFMhPFE0Si2m97fkThwimCa2FaOi3ZESf30P8h59-B2m1TfjJR20S9k1cQ6ZCSemit7mmwvucpKA9fHL3HQofswOnAtVVky2QWk6WNJER85vWWdhXKtd6n5KLCwKyvWc7MrEgA3aEus1D1l7VtcG-UR7N9rl_RlVWSssx7RH8zFFUA3sSJapT8jdeziker_IFEmlPWeLIoEe_z9Y-BX-hcOEyUiQEMy7BjxENskJjZvTCa9aWpLDjQraLB5w9eyY4HH3wKXo8Y"/>
          <h1 className="font-display-lg text-display-lg text-gradient-primary mt-sm">Weekly Pulse</h1>
        </div>
        <p className="font-body-base text-body-base text-on-surface-variant max-w-2xl mt-xs">Generate AI-powered product insights from App Store and Play Store reviews in seconds.</p>
      </header>

      <main className="flex-grow w-full max-w-container-max mx-auto px-gutter pb-2xl flex flex-col items-center z-10 relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[400px] bg-primary/5 blur-[120px] rounded-full pointer-events-none -z-10"></div>
        
        <form onSubmit={handleGenerate} className="w-full max-w-3xl mt-md mb-2xl relative group">
          <div className="relative flex items-center w-full">
            <span className="material-symbols-outlined absolute left-lg text-outline-variant group-focus-within:text-primary transition-colors z-10">search</span>
            <input 
              className="w-full h-16 pl-2xl pr-[140px] rounded-xl glass-input text-black font-body-base text-body-base placeholder:text-outline-variant" 
              placeholder="e.g. Groww, WhatsApp, Spotify" 
              type="text" 
              value={appName}
              onChange={(e) => setAppName(e.target.value)}
              required
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={loading}
              className="absolute right-xs top-1/2 -translate-y-1/2 h-14 px-md bg-accent-gradient rounded-lg text-white font-label-caps text-label-caps uppercase flex items-center gap-xs neon-glow-primary transition-all active:scale-95 z-10 disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="material-symbols-outlined text-[18px] animate-spin" style={{ animation: 'spin 1s linear infinite' }}>sync</span>
              ) : (
                <span className="material-symbols-outlined text-[18px]">bolt</span>
              )}
              {loading ? 'Analyzing...' : 'Generate Pulse'}
            </button>
          </div>
        </form>

        {error && (
          <div className="w-full max-w-3xl mb-lg glass-surface p-md rounded-lg border-l-4 border-l-error bg-error-container/10 flex items-center gap-sm">
            <span className="material-symbols-outlined text-error text-[18px]">error</span>
            <span className="text-sm text-on-surface-variant">{error}</span>
          </div>
        )}

        {result && !loading && (
          <div className="w-full flex flex-col gap-xl">
            <div className="flex justify-end gap-sm w-full">
              {result.doc_url && (
                <a href={result.doc_url} target="_blank" rel="noreferrer" className="glass-surface h-10 px-md rounded-full flex items-center gap-sm font-label-caps text-label-caps text-on-surface hover:bg-white/5 transition-colors">
                  <span className="material-symbols-outlined text-[16px]">description</span>
                  View Google Doc
                </a>
              )}
              {result.email_confirmation && (
                <div className="glass-surface h-10 px-md rounded-full flex items-center gap-sm font-label-caps text-label-caps text-[#A3E635] border-[#A3E635]/30 bg-[#A3E635]/5">
                  <span className="material-symbols-outlined text-[16px]">check_circle</span>
                  {result.email_confirmation}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-md w-full">
              <div className="glass-surface metric-card p-lg rounded-xl flex flex-col gap-xs">
                <div className="flex items-center gap-xs text-on-surface-variant font-label-caps text-label-caps uppercase">
                  <span className="material-symbols-outlined text-[16px] text-[#34A853]">shop</span>
                  Play Store
                </div>
                <div className="font-headline-md text-headline-md text-on-surface flex items-baseline gap-xs">
                  {result.play_store_id || 'N/A'}
                </div>
              </div>
              
              <div className="glass-surface metric-card p-lg rounded-xl flex flex-col gap-xs">
                <div className="flex items-center gap-xs text-on-surface-variant font-label-caps text-label-caps uppercase">
                  <span className="material-symbols-outlined text-[16px] text-[#007AFF]">apps</span>
                  App Store
                </div>
                <div className="font-headline-md text-headline-md text-on-surface flex items-baseline gap-xs">
                  {result.app_store_id || 'N/A'}
                </div>
              </div>

              <div className="glass-surface metric-card p-lg rounded-xl flex flex-col gap-xs">
                <div className="flex items-center gap-xs text-on-surface-variant font-label-caps text-label-caps uppercase">
                  <span className="material-symbols-outlined text-[16px]">analytics</span>
                  Analyzed
                </div>
                <div className="font-headline-md text-headline-md text-on-surface">
                  {result.reviews_analyzed} <span className="text-body-sm font-body-sm text-on-surface-variant font-normal">reviews</span>
                </div>
              </div>

              <div className="glass-surface metric-card p-lg rounded-xl flex flex-col gap-xs">
                <div className="flex items-center gap-xs text-on-surface-variant font-label-caps text-label-caps uppercase">
                  <span className="material-symbols-outlined text-[16px]">category</span>
                  Themes
                </div>
                <div className="font-headline-md text-headline-md text-on-surface">
                  {result.themes_found} <span className="text-body-sm font-body-sm text-on-surface-variant font-normal">identified</span>
                </div>
              </div>
            </div>

            <div className="w-full glass-surface rounded-xl p-0 overflow-hidden flex flex-col border border-outline-variant/30 mt-sm shadow-[0_10px_30px_rgba(0,0,0,0.5)]">
              <div className="border-b border-white/5 bg-surface-container/50 px-lg py-md flex items-center justify-between">
                <h2 className="font-headline-md text-headline-md text-on-surface flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary">auto_awesome</span>
                  Generated Report
                </h2>
                <div className="flex gap-xs">
                  <span className="w-3 h-3 rounded-full bg-error/80"></span>
                  <span className="w-3 h-3 rounded-full bg-secondary/80"></span>
                  <span className="w-3 h-3 rounded-full bg-[#A3E635]/80"></span>
                </div>
              </div>
              
              <div className="p-lg md:p-[40px] bg-surface-lowest text-on-surface font-body-base text-body-base leading-relaxed flex flex-col gap-md max-w-[800px] mx-auto w-full markdown-body">
                <style>{`
                  .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 {
                    color: #d0bcff;
                    margin-top: 1.5rem;
                    margin-bottom: 0.5rem;
                  }
                  .markdown-body h1 { font-size: 2rem; font-weight: 700; }
                  .markdown-body h2 { font-size: 1.5rem; font-weight: 600; }
                  .markdown-body h3 { font-size: 1.25rem; font-weight: 600; }
                  .markdown-body p { margin-bottom: 1rem; color: #cbc3d7; }
                  .markdown-body ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1rem; color: #cbc3d7; }
                  .markdown-body li { margin-bottom: 0.25rem; }
                  .markdown-body strong { color: #dae2fd; font-weight: 600; }
                `}</style>
                <ReactMarkdown>{result.doc_content}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </main>


    </>
  )
}

export default App
