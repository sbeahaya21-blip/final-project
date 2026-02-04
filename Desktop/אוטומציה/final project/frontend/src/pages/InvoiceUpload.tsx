import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { invoiceApi, Invoice, AnomalyResult } from '../services/api'
import './InvoiceUpload.css'

function InvoiceUpload() {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [analysis, setAnalysis] = useState<AnomalyResult | null>(null)
  const navigate = useNavigate()

  const handleFile = useCallback(async (file: File) => {
    if (!file) return

    setIsUploading(true)
    setError(null)
    setInvoice(null)
    setAnalysis(null)

    try {
      console.log('=== UPLOAD DEBUG ===')
      console.log('File:', file.name)
      // Upload and parse invoice (no auto-sync - use submit button instead)
      const uploadedInvoice = await invoiceApi.uploadInvoice(file, false)
      console.log('Invoice uploaded successfully:', uploadedInvoice.id)
      setInvoice(uploadedInvoice)

      // Analyze invoice
      setIsUploading(false)
      setIsAnalyzing(true)
      console.log('Analyzing invoice:', uploadedInvoice.id)
      const analysisResult = await invoiceApi.analyzeInvoice(uploadedInvoice.id)
      console.log('Analysis complete:', analysisResult)
      setAnalysis(analysisResult)
      setIsAnalyzing(false)
    } catch (err: any) {
      console.error('Error processing invoice:', err)
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to process invoice. Please check if the backend server is running.'
      setError(errorMessage)
      setIsUploading(false)
      setIsAnalyzing(false)
    }
  }, []) // Removed syncToERPNext dependency

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }, [handleFile])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }, [handleFile])

  const getRiskClass = (score: number) => {
    if (score >= 70) return 'high'
    if (score >= 50) return 'medium'
    return 'low'
  }

  return (
    <div className="invoice-upload">
      <div className="upload-header">
        <h1>Upload Invoice</h1>
        <p className="subtitle">Upload an invoice to detect anomalies and potential fraud</p>
      </div>

      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${isUploading || isAnalyzing ? 'processing' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📄</div>
          <p className="upload-text">
            {isUploading || isAnalyzing
              ? isUploading
                ? 'Processing invoice...'
                : 'Analyzing for anomalies...'
              : 'Drag and drop an invoice file here, or click to browse'}
          </p>
          <label htmlFor="file-input" className="upload-button">
            Choose File
          </label>
          <input
            id="file-input"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.txt"
            onChange={handleFileInput}
            disabled={isUploading || isAnalyzing}
            style={{ display: 'none' }}
          />
        </div>
      </div>

      {error && (
        <div className="error-message" style={{ 
          marginTop: '20px', 
          padding: '15px', 
          backgroundColor: '#fee', 
          border: '1px solid #fcc', 
          borderRadius: '4px',
          color: '#c33'
        }}>
          <strong>⚠️ Error:</strong> {error}
          <br />
          <small style={{ marginTop: '10px', display: 'block' }}>
            Make sure the backend server is running at http://localhost:8000
          </small>
        </div>
      )}

      {invoice && analysis && (
        <div className="analysis-results">
          <div className={`result-card ${analysis.is_suspicious ? 'suspicious' : 'safe'}`}>
            <div className="result-header">
              <h2>Analysis Results</h2>
              <div className={`risk-badge ${getRiskClass(analysis.risk_score)}`}>
                {analysis.is_suspicious ? '⚠️ SUSPICIOUS' : '✓ SAFE'}
              </div>
            </div>

            <div className={`risk-score ${getRiskClass(analysis.risk_score)}`}>
              Risk Score: {analysis.risk_score}/100
            </div>

            {analysis.anomalies.length > 0 && (
              <div className="anomalies-section">
                <h3>Detected Anomalies ({analysis.anomalies.length})</h3>
                <div className="anomalies-list">
                  {analysis.anomalies.map((anomaly, index) => (
                    <div key={index} className="anomaly-item">
                      <div className="anomaly-header">
                        <span className="anomaly-type">
                          {anomaly.type.replace('_', ' ').toUpperCase()}
                        </span>
                        {anomaly.item_name && (
                          <span className="anomaly-item-name">{anomaly.item_name}</span>
                        )}
                        <span className="anomaly-severity">Severity: {anomaly.severity}/100</span>
                      </div>
                      <p className="anomaly-description">{anomaly.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="explanation-box">
              <h3>Explanation</h3>
              <p>{analysis.explanation}</p>
            </div>

            <div className="invoice-details">
              <h3>Invoice Details</h3>
              <div className="details-grid">
                <div className="detail-item">
                  <span className="detail-label">Vendor:</span>
                  <span className="detail-value">{invoice.parsed_data.vendor_name}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Invoice #:</span>
                  <span className="detail-value">{invoice.parsed_data.invoice_number}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Date:</span>
                  <span className="detail-value">
                    {new Date(invoice.parsed_data.invoice_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Total Amount:</span>
                  <span className="detail-value">
                    ${invoice.parsed_data.total_amount.toFixed(2)} {invoice.parsed_data.currency}
                  </span>
                </div>
              </div>

              <div className="items-table">
                <h4>Items</h4>
                <table>
                  <thead>
                    <tr>
                      <th>Item Name</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoice.parsed_data.items.map((item, index) => (
                      <tr key={index}>
                        <td>{item.name}</td>
                        <td>{item.quantity}</td>
                        <td>${item.unit_price.toFixed(2)}</td>
                        <td>${item.total_price.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="action-buttons">
                <button
                  className="btn btn-primary"
                  onClick={() => navigate(`/invoices/${invoice.id}`)}
                >
                  View Details
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setInvoice(null)
                    setAnalysis(null)
                    setError(null)
                  }}
                >
                  Upload Another
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InvoiceUpload
