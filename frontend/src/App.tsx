import React, { useState, useEffect } from 'react'

export default function App() {
  const [status, setStatus] = useState<string>('Connecting...')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setStatus(data.status || 'Active'))
      .catch(() => setStatus('Backend Offline'))
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Alpaca AI — Trading Council & Execution</h1>
      <p>Backend Status: <strong>{status}</strong></p>
    </div>
  )
}
