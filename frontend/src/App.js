import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import PersistencePrediction from './components/PersistencePrediction';
import GPAPrediction from './components/GPAPrediction';
import AtRiskPrediction from './components/AtRiskPrediction';
import AcademicPipeline from './components/AcademicPipeline';
import DataExplorer from './components/DataExplorer';
import ModelMetrics from './components/ModelMetrics';
import AdminPanel from './components/AdminPanel';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/predict/persistence" element={<PersistencePrediction />} />
            <Route path="/predict/gpa" element={<GPAPrediction />} />
            <Route path="/predict/atrisk" element={<AtRiskPrediction />} />
            <Route path="/predict/pipeline" element={<AcademicPipeline />} />
            <Route path="/data" element={<DataExplorer />} />
            <Route path="/models" element={<ModelMetrics />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
