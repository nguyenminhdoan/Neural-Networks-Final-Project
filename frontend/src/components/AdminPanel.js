import React, { useState, useEffect } from 'react';
import { retrainModels, getPredictionHistory, reimportData, getModelMetrics } from '../services/api';

function AdminPanel() {
  const [logs, setLogs] = useState(null);
  const [logPage, setLogPage] = useState(1);
  const [retraining, setRetraining] = useState(false);
  const [reimporting, setReimporting] = useState(false);
  const [message, setMessage] = useState('');
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    loadLogs();
    getModelMetrics().then(res => setMetrics(res.data)).catch(console.error);
  }, []);

  useEffect(() => {
    loadLogs();
  }, [logPage]);

  const loadLogs = () => {
    getPredictionHistory(logPage)
      .then(res => setLogs(res.data))
      .catch(console.error);
  };

  const handleRetrain = async () => {
    if (!window.confirm('This will retrain all neural network models. This may take a few minutes. Continue?')) return;
    setRetraining(true);
    setMessage('');
    try {
      const res = await retrainModels();
      setMessage('Models retrained successfully!');
      setMetrics(res.data.metrics || null);
      getModelMetrics().then(r => setMetrics(r.data)).catch(console.error);
    } catch (err) {
      setMessage('Retraining failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setRetraining(false);
    }
  };

  const handleReimport = async () => {
    if (!window.confirm('This will delete all existing data and reimport from CSV. Continue?')) return;
    setReimporting(true);
    setMessage('');
    try {
      const res = await reimportData();
      setMessage(res.data.message);
    } catch (err) {
      setMessage('Import failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setReimporting(false);
    }
  };

  const parseJSON = (str) => {
    try { return JSON.parse(str); } catch { return str; }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Administration Panel</h1>
        <p>Manage models, data, and view prediction history</p>
      </div>

      {message && (
        <div className={message.includes('failed') ? 'error-msg' : 'card'}
             style={!message.includes('failed') ? { background: 'rgba(6, 214, 160, 0.1)', border: '1px solid #06d6a0', color: '#06d6a0', marginBottom: '24px', padding: '12px 16px', borderRadius: '8px' } : { marginBottom: '24px' }}>
          {message}
        </div>
      )}

      {/* Admin Actions */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="card">
          <h2>Model Management</h2>
          <p style={{ color: '#a0a0b8', fontSize: '0.9rem', marginBottom: '16px' }}>
            Retrain all neural network models with the latest data. This will
            replace the existing trained models.
          </p>
          {metrics && metrics.models_ready && (
            <div style={{ marginBottom: '16px', fontSize: '0.85rem', color: '#a0a0b8' }}>
              <div>Persistence Accuracy: <strong style={{ color: '#4361ee' }}>{(metrics.persistence?.accuracy * 100).toFixed(1)}%</strong></div>
              <div>GPA R2 Score: <strong style={{ color: '#06d6a0' }}>{metrics.gpa?.r2_score?.toFixed(3)}</strong></div>
              <div>At-Risk Accuracy: <strong style={{ color: '#f72585' }}>{(metrics.at_risk?.accuracy * 100).toFixed(1)}%</strong></div>
            </div>
          )}
          <button className="btn btn-primary" onClick={handleRetrain} disabled={retraining}>
            {retraining ? 'Retraining... (this may take a minute)' : 'Retrain All Models'}
          </button>
        </div>

        <div className="card">
          <h2>Data Management</h2>
          <p style={{ color: '#a0a0b8', fontSize: '0.9rem', marginBottom: '16px' }}>
            Reimport student data from the CSV file. This will replace all
            existing records in the database.
          </p>
          <button className="btn btn-danger" onClick={handleReimport} disabled={reimporting}>
            {reimporting ? 'Importing...' : 'Reimport Data from CSV'}
          </button>
        </div>
      </div>

      {/* Prediction History */}
      <div className="card">
        <h2>Prediction History</h2>
        {logs && logs.logs.length > 0 ? (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Model</th>
                    <th>Result</th>
                    <th>Confidence</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.logs.map(log => {
                    const result = parseJSON(log.prediction_result);
                    return (
                      <tr key={log.id}>
                        <td>{log.id}</td>
                        <td>
                          <span className="badge badge-info">
                            {log.model_type}
                          </span>
                        </td>
                        <td>
                          {typeof result === 'object'
                            ? (result.label || result.predicted_gpa || JSON.stringify(result))
                            : result}
                        </td>
                        <td>
                          {log.confidence !== null
                            ? `${(log.confidence * 100).toFixed(1)}%`
                            : '-'}
                        </td>
                        <td style={{ fontSize: '0.85rem', color: '#a0a0b8' }}>
                          {log.created_at ? new Date(log.created_at).toLocaleString() : '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <button onClick={() => setLogPage(p => p - 1)} disabled={logPage <= 1}>
                Previous
              </button>
              <span>Page {logs.current_page} of {logs.pages}</span>
              <button onClick={() => setLogPage(p => p + 1)} disabled={logPage >= logs.pages}>
                Next
              </button>
            </div>
          </>
        ) : (
          <p style={{ color: '#a0a0b8', textAlign: 'center', padding: '40px' }}>
            No predictions have been made yet. Use the prediction pages to generate results.
          </p>
        )}
      </div>
    </div>
  );
}

export default AdminPanel;
