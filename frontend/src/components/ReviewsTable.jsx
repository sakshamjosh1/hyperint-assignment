import React from 'react'

export default function ReviewsTable({ reviews }) {
  if (!reviews || reviews.length === 0) {
    return <div className="center">No reviews yet. Submit one via WhatsApp!</div>
  }

  return (
    <div className="table-wrap">
      <table className="reviews-table" role="table">
        <thead>
          <tr>
            <th>User</th>
            <th>Phone</th>
            <th>Product</th>
            <th>Review</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map((r) => (
            <tr key={r.id}>
              <td>{r.user_name || '—'}</td>
              <td>{r.phone || '—'}</td>
              <td>{r.product_name || '—'}</td>
              <td>{r.review_text || '—'}</td>
              <td>{r.created_at ? new Date(r.created_at).toLocaleString() : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
