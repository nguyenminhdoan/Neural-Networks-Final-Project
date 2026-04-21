import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import { getModelMetrics } from '../services/api';

function ModelMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [activeTab, setActiveTab] = useState('persistence');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelMetrics()
      .then(res => setMetrics(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading model metrics...</div>;
  }

  if (!metrics || !metrics.models_ready) {
    return <div className="error-msg">Models are not trained yet. Visit Admin panel to train.</div>;
  }

  const tabs = [
    { key: 'persistence', label: 'Persistence Model' },
    { key: 'gpa', label: 'GPA Model' },
    { key: 'at_risk', label: 'At-Risk Model' },
    { key: 'stacked', label: 'Stacked Academic Model' },
  ];

  const current = metrics[activeTab];
  const isRegression = activeTab === 'gpa' || activeTab === 'stacked';

  const buildChartData = (history, lossKey, valLossKey) => {
    if (!history) return [];
    return history[lossKey].map((v, i) => ({
      epoch: i + 1,
      training: Number(v.toFixed(4)),
      validation: Number(history[valLossKey][i].toFixed(4)),
    }));
  };

  const lossData = buildChartData(current?.training_history, 'loss', 'val_loss');

  const accData = isRegression
    ? buildChartData(current?.training_history, 'mae', 'val_mae')
    : buildChartData(current?.training_history, 'accuracy', 'val_accuracy');

  const renderConfusionMatrix = (cm) => {
    if (!cm) return null;
    return (
      <div style={{ marginTop: '16px' }}>
        <h3>Confusion Matrix</h3>
        <table className="data-table" style={{ maxWidth: '300px' }}>
          <thead>
            <tr>
              <th></th>
              <th>Pred: 0</th>
              <th>Pred: 1</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Actual: 0</strong></td>
              <td style={{ color: '#06d6a0', fontWeight: 600 }}>{cm[0][0]}</td>
              <td style={{ color: '#ef476f', fontWeight: 600 }}>{cm[0][1]}</td>
            </tr>
            <tr>
              <td><strong>Actual: 1</strong></td>
              <td style={{ color: '#ef476f', fontWeight: 600 }}>{cm[1][0]}</td>
              <td style={{ color: '#06d6a0', fontWeight: 600 }}>{cm[1][1]}</td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div>
      <div className="page-header">
        <h1>Model Performance Metrics</h1>
        <p>Training history and evaluation results for all neural network models</p>
      </div>

      <div className="tabs">
        {tabs.map(tab => (
          <button key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Performance Metrics */}
      <div className="grid-4" style={{ marginBottom: '24px' }}>
        {isRegression ? (
          <>
            <div className="stat-card">
              <div className="stat-value">{current.r2_score?.toFixed(3)}</div>
              <div className="stat-label">R2 Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{current.mae?.toFixed(3)}</div>
              <div className="stat-label">MAE</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{current.rmse?.toFixed(3)}</div>
              <div className="stat-label">RMSE</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{current.mse?.toFixed(4)}</div>
              <div className="stat-label">MSE</div>
            </div>
          </>
        ) : (
          <>
            <div className="stat-card">
              <div className="stat-value">{(current.accuracy * 100).toFixed(1)}%</div>
              <div className="stat-label">Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{(current.precision * 100).toFixed(1)}%</div>
              <div className="stat-label">Precision</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{(current.recall * 100).toFixed(1)}%</div>
              <div className="stat-label">Recall</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{current.f1_score?.toFixed(3)}</div>
              <div className="stat-label">F1 Score</div>
            </div>
          </>
        )}
      </div>

      {/* Training Details */}
      <div className="grid-3" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-value">{current.training_samples}</div>
          <div className="stat-label">Training Samples</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{current.test_samples}</div>
          <div className="stat-label">Test Samples</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{current.epochs_trained}</div>
          <div className="stat-label">Epochs Trained</div>
        </div>
      </div>

      {/* Training Charts */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        <div className="card">
          <h2>Training & Validation Loss</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={lossData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="epoch" tick={{ fill: '#a0a0b8' }} label={{ value: 'Epoch', fill: '#a0a0b8', position: 'bottom' }} />
              <YAxis tick={{ fill: '#a0a0b8' }} />
              <Tooltip contentStyle={{ background: '#16213e', border: '1px solid #2a2a4a' }} />
              <Legend />
              <Line type="monotone" dataKey="training" stroke="#4361ee" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="validation" stroke="#f72585" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>{isRegression ? 'Training & Validation MAE' : 'Training & Validation Accuracy'}</h2>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={accData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
              <XAxis dataKey="epoch" tick={{ fill: '#a0a0b8' }} label={{ value: 'Epoch', fill: '#a0a0b8', position: 'bottom' }} />
              <YAxis tick={{ fill: '#a0a0b8' }} />
              <Tooltip contentStyle={{ background: '#16213e', border: '1px solid #2a2a4a' }} />
              <Legend />
              <Line type="monotone" dataKey="training" stroke="#06d6a0" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="validation" stroke="#ffd166" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confusion Matrix (for classification models only) */}
      {!isRegression && current.confusion_matrix && (
        <div className="card">
          {renderConfusionMatrix(current.confusion_matrix)}
        </div>
      )}
    </div>
  );
}

export default ModelMetrics;
