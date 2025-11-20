import { useEffect, useState } from 'react'
import axios from 'axios'
import ReviewsTable from './components/ReviewsTable'
import { API_BASE } from './config'

export default function App() {
  const [reviews, setReviews] = useState(null) // null = loading
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    axios
      .get(`${API_BASE}/api/reviews`)
      .then((res) => {
        if (mounted) setReviews(res.data.reviews || [])
      })
      .catch((err) => {
        if (mounted) setError(err.response?.data || err.message || 'Failed to fetch')
      })
    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="container">
      <header>
        <h1>Product Reviews</h1>
        <p className="subtitle">Collected via WhatsApp — powered by your FastAPI backend</p>
      </header>

      {reviews === null ? (
        <div className="center">Loading reviews...</div>
      ) : error ? (
        <div className="error">Error: {typeof error === 'string' ? error : JSON.stringify(error)}</div>
      ) : (
        <ReviewsTable reviews={reviews} />
      )}

      <footer>
        <small>Built for Hyperint — Saksham</small>
      </footer>
    </div>
  )
}
