import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { invoiceApi, Invoice } from '../services/api'
import './InvoiceList.css'

function InvoiceList() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadInvoices()
  }, [])

  const loadInvoices = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await invoiceApi.listInvoices()
      // Sort by uploaded_at descending (newest first)
      data.sort((a, b) => 
        new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime()
      )
      setInvoices(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load invoices')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (invoiceId: string, invoiceNumber: string) => {
    if (!window.confirm(`Are you sure you want to delete invoice ${invoiceNumber}?`)) {
      return
    }

    try {
      await invoiceApi.deleteInvoice(invoiceId)
      // Reload the list
      await loadInvoices()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to delete invoice')
    }
  }

  const getRiskClass = (score?: number) => {
    if (!score) return 'unknown'
    if (score >= 70) return 'high'
    if (score >= 50) return 'medium'
    return 'low'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="invoice-list">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading invoices...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="invoice-list">
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button className="retry-button" onClick={loadInvoices}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="invoice-list">
      <div className="list-header">
        <h1>All Invoices</h1>
        <button className="btn btn-primary" onClick={loadInvoices}>
          Refresh
        </button>
      </div>

      {invoices.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h2>No invoices yet</h2>
          <p>Upload your first invoice to get started</p>
          <Link to="/" className="btn btn-primary">
            Upload Invoice
          </Link>
        </div>
      ) : (
        <div className="invoices-grid">
          {invoices.map((invoice) => (
            <Link
              key={invoice.id}
              to={`/invoices/${invoice.id}`}
              className="invoice-card-link"
            >
              <div className={`invoice-card ${invoice.is_suspicious ? 'suspicious' : 'safe'}`}>
                <div className="card-header">
                  <div className="vendor-info">
                    <h3>{invoice.parsed_data.vendor_name}</h3>
                    <span className="invoice-number">
                      {invoice.parsed_data.invoice_number}
                    </span>
                  </div>
                  {invoice.is_suspicious && (
                    <span className="suspicious-badge">⚠️ Suspicious</span>
                  )}
                </div>

                <div className="card-body">
                  <div className="card-details">
                    <div className="detail-row">
                      <span className="label">Date:</span>
                      <span className="value">
                        {new Date(invoice.parsed_data.invoice_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Amount:</span>
                      <span className="value amount">
                        ${invoice.parsed_data.total_amount.toFixed(2)}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Items:</span>
                      <span className="value">
                        {invoice.parsed_data.items.length} item(s)
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Uploaded:</span>
                      <span className="value">
                        {formatDate(invoice.uploaded_at)}
                      </span>
                    </div>
                  </div>

                  {invoice.risk_score !== undefined && (
                    <div className="risk-section">
                      <div className="risk-label">Risk Score</div>
                      <div className={`risk-score ${getRiskClass(invoice.risk_score)}`}>
                        {invoice.risk_score}/100
                      </div>
                    </div>
                  )}
                </div>

                <div className="card-footer">
                  <div className="card-actions">
                    <Link to={`/invoices/${invoice.id}`} className="view-link">
                      View Details →
                    </Link>
                    <button
                      className="delete-btn"
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        handleDelete(invoice.id, invoice.parsed_data.invoice_number)
                      }}
                      title="Delete invoice"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default InvoiceList
