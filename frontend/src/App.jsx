import { useState, useEffect } from 'react'

const API_BASE = '/api/v1'

const styles = {
  container: { maxWidth: '1400px', margin: '0 auto', padding: '20px' },
  card: {
    background: '#0d0d18',
    border: '1px solid #1c1c30',
    borderRadius: '12px',
    padding: '20px',
    cursor: 'pointer',
    transition: 'all 0.3s ease'
  },
  button: {
    background: '#6366f1',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontFamily: 'inherit'
  },
  input: {
    width: '100%',
    padding: '12px',
    background: '#0d0d18',
    border: '1px solid #1c1c30',
    borderRadius: '8px',
    color: '#e0e0e0',
    fontFamily: 'inherit',
    fontSize: '14px'
  }
}

function StarRating({ rating, onRate, interactive = false }) {
  const [hover, setHover] = useState(0)
  return (
    <div style={{ display: 'flex', gap: '4px' }}>
      {[1, 2, 3, 4, 5].map(star => (
        <span
          key={star}
          onClick={() => interactive && onRate(star)}
          onMouseEnter={() => interactive && setHover(star)}
          onMouseLeave={() => interactive && setHover(0)}
          style={{
            cursor: interactive ? 'pointer' : 'default',
            color: star <= (hover || rating) ? '#fbbf24' : '#4b5563',
            fontSize: '24px'
          }}
        >
          ★
        </span>
      ))}
    </div>
  )
}

function HomePage({ onSelectSystem }) {
  const [systems, setSystems] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchSystems = async (q = '') => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`)
      const data = await res.json()
      setSystems(data.systems || [])
    } catch (err) {
      console.error('Failed to fetch systems:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSystems() }, [])

  return (
    <div style={styles.container}>
      <h1 style={{ color: '#6366f1', textAlign: 'center', marginBottom: '32px', fontSize: '36px' }}>
        ⚡ NexusAPI Marketplace
      </h1>
      
      <div style={{ marginBottom: '32px' }}>
        <input
          type="text"
          placeholder="Search by title, tech stack, or description..."
          value={search}
          onChange={e => {
            setSearch(e.target.value)
            fetchSystems(e.target.value)
          }}
          style={styles.input}
        />
      </div>

      {loading ? (
        <p style={{ textAlign: 'center', color: '#9ca3af' }}>Loading systems...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
          {systems.map(sys => (
            <div
              key={sys.id}
              onClick={() => onSelectSystem(sys.slug)}
              style={styles.card}
              onMouseEnter={e => e.currentTarget.style.borderColor = '#6366f1'}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#1c1c30'}
            >
              <h3 style={{ color: '#00d2d3', marginBottom: '8px', fontSize: '20px' }}>{sys.title}</h3>
              <p style={{ color: '#9ca3af', fontSize: '14px', marginBottom: '12px' }}>
                {sys.description?.substring(0, 100)}...
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                {sys.tech_stack?.map(tech => (
                  <span key={tech} style={{
                    background: '#1e1e2f',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#6366f1'
                  }}>
                    {tech}
                  </span>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <StarRating rating={parseFloat(sys.rating) || 0} />
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>
                  ⬇️ {sys.downloads || 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function SystemDetail({ slug, onBack }) {
  const [system, setSystem] = useState(null)
  const [files, setFiles] = useState({})
  const [activeFile, setActiveFile] = useState('')
  const [activeTab, setActiveTab] = useState('overview')
  const [reviews, setReviews] = useState([])
  const [newRating, setNewRating] = useState(0)
  const [newComment, setNewComment] = useState('')

  useEffect(() => {
    const loadSystem = async () => {
      try {
        const [sysRes, filesRes, reviewsRes] = await Promise.all([
          fetch(`${API_BASE}/systems/${slug}`),
          fetch(`${API_BASE}/systems/${slug}/files`),
          fetch(`${API_BASE}/systems/${slug}/reviews`)
        ])
        
        const sysData = await sysRes.json()
        const filesData = await filesRes.json()
        const reviewsData = await reviewsRes.json()
        
        setSystem(sysData.system)
        setFiles(filesData.files || {})
        setReviews(reviewsData.reviews || [])
        
        const fileKeys = Object.keys(filesData.files || {})
        if (fileKeys.length > 0) setActiveFile(fileKeys[0])
      } catch (err) {
        console.error('Failed to load system:', err)
      }
    }
    loadSystem()
  }, [slug])

  const submitReview = async () => {
    if (!newRating || !newComment.trim()) return
    try {
      const res = await fetch(`${API_BASE}/systems/${slug}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating: newRating, comment: newComment })
      })
      if (res.ok) {
        const updatedReviews = await fetch(`${API_BASE}/systems/${slug}/reviews`)
        const data = await updatedReviews.json()
        setReviews(data.reviews || [])
        setNewRating(0)
        setNewComment('')
      }
    } catch (err) {
      console.error('Failed to submit review:', err)
    }
  }

  const copyCode = () => {
    if (activeFile && files[activeFile]) {
      navigator.clipboard.writeText(files[activeFile])
      alert('Code copied to clipboard!')
    }
  }

  if (!system) return <div style={styles.container}><p>Loading...</p></div>

  return (
    <div style={styles.container}>
      <button onClick={onBack} style={{
        ...styles.button,
        background: 'transparent',
        border: '1px solid #1c1c30',
        marginBottom: '20px'
      }}>
        ← Back to Marketplace
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '30px' }}>
        <div>
          <h2 style={{ color: '#00d2d3', fontSize: '32px' }}>{system.title}</h2>
          <p style={{ color: '#9ca3af', marginTop: '8px' }}>
            Category: {system.category} • Setup: {system.setup_time}
          </p>
        </div>
        <a href={`${API_BASE}/download/${slug}`} style={{
          ...styles.button,
          textDecoration: 'none',
          display: 'inline-block'
        }}>
          📥 Download .zip
        </a>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '20px', borderBottom: '1px solid #1c1c30', marginBottom: '24px' }}>
        {['overview', 'reviews', 'files'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              background: 'transparent',
              border: 'none',
              color: activeTab === tab ? '#6366f1' : '#9ca3af',
              padding: '12px 20px',
              borderBottom: activeTab === tab ? '2px solid #6366f1' : '2px solid transparent',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontFamily: 'inherit',
              fontSize: '16px'
            }}
          >
            {tab === 'overview' ? '📋 Overview' : tab === 'reviews' ? '💬 Reviews' : '📁 Files'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div style={styles.card}>
          <p style={{ color: '#e0e0e0', lineHeight: '1.8', marginBottom: '20px' }}>{system.description}</p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {system.tech_stack?.map(tech => (
              <span key={tech} style={{
                background: '#1e1e2f',
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '14px',
                color: '#6366f1'
              }}>
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Reviews Tab */}
      {activeTab === 'reviews' && (
        <div>
          <div style={{ marginBottom: '30px' }}>
            {reviews.length === 0 ? (
              <p style={{ color: '#9ca3af' }}>No reviews yet. Be the first to review!</p>
            ) : (
              reviews.map((review, idx) => (
                <div key={idx} style={{ ...styles.card, marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <strong style={{ color: '#00d2d3' }}>{review.user_name}</strong>
                    <StarRating rating={review.rating} />
                  </div>
                  <p style={{ color: '#e0e0e0' }}>{review.comment}</p>
                </div>
              ))
            )}
          </div>

          <div style={styles.card}>
            <h3 style={{ color: '#6366f1', marginBottom: '16px' }}>Add Your Review</h3>
            <div style={{ marginBottom: '12px' }}>
              <StarRating rating={newRating} onRate={setNewRating} interactive />
            </div>
            <textarea
              value={newComment}
              onChange={e => setNewComment(e.target.value)}
              placeholder="Write your experience..."
              rows={3}
              style={{ ...styles.input, marginBottom: '12px', resize: 'vertical' }}
            />
            <button onClick={submitReview} style={styles.button}>
              Submit Review
            </button>
          </div>
        </div>
      )}

      {/* Files Tab */}
      {activeTab === 'files' && (
        <div style={{ display: 'flex', gap: '20px', height: '70vh' }}>
          <div style={{
            width: '250px',
            ...styles.card,
            overflowY: 'auto'
          }}>
            <h3 style={{ color: '#6366f1', marginBottom: '16px' }}>📁 Files</h3>
            {Object.keys(files).map(fileName => (
              <div
                key={fileName}
                onClick={() => setActiveFile(fileName)}
                style={{
                  padding: '8px 12px',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  marginBottom: '4px',
                  background: activeFile === fileName ? '#6366f1' : 'transparent',
                  color: activeFile === fileName ? 'white' : '#9ca3af',
                  fontSize: '13px',
                  fontFamily: 'monospace'
                }}
              >
                {fileName}
              </div>
            ))}
          </div>

          <div style={{ flex: 1, ...styles.card, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>{activeFile}</span>
              <button onClick={copyCode} style={{
                background: '#1e1e2f',
                color: '#e0e0e0',
                border: 'none',
                padding: '6px 12px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px',
                fontFamily: 'inherit'
              }}>
                📋 Copy
              </button>
            </div>
            <pre style={{
              flex: 1,
              background: '#05050a',
              padding: '20px',
              borderRadius: '8px',
              overflow: 'auto',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#00ff88',
              fontFamily: 'monospace',
              border: '1px solid #1c1c30'
            }}>
              {files[activeFile] || 'Select a file to view its contents'}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [currentSlug, setCurrentSlug] = useState(null)

  return currentSlug ? (
    <SystemDetail slug={currentSlug} onBack={() => setCurrentSlug(null)} />
  ) : (
    <HomePage onSelectSystem={setCurrentSlug} />
  )
}
