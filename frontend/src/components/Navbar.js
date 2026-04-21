import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const navLinks = [
  { path: '/', label: 'Dashboard' },
  { path: '/predict/persistence', label: 'Persistence' },
  { path: '/predict/gpa', label: 'GPA Prediction' },
  { path: '/predict/atrisk', label: 'At-Risk' },
  { path: '/predict/pipeline', label: 'Academic Pipeline' },
  { path: '/data', label: 'Data Explorer' },
  { path: '/models', label: 'Model Metrics' },
  { path: '/admin', label: 'Admin' },
];

function Navbar() {
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav style={styles.nav}>
      <div style={styles.container}>
        <Link to="/" style={styles.brand}>
          <span style={styles.brandIcon}>&#9733;</span>
          Student Analytics AI
        </Link>

        <button style={styles.menuToggle} onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? '\u2715' : '\u2630'}
        </button>

        <div style={{ ...styles.links, ...(menuOpen ? styles.linksOpen : {}) }}>
          {navLinks.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              onClick={() => setMenuOpen(false)}
              style={{
                ...styles.link,
                ...(location.pathname === path ? styles.activeLink : {}),
              }}
            >
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

const styles = {
  nav: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    background: 'rgba(22, 33, 62, 0.95)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid #2a2a4a',
    zIndex: 1000,
  },
  container: {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '56px',
  },
  brand: {
    color: '#e8e8e8',
    textDecoration: 'none',
    fontSize: '1.1rem',
    fontWeight: 700,
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  brandIcon: {
    color: '#4361ee',
    fontSize: '1.3rem',
  },
  links: {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
  },
  linksOpen: {},
  link: {
    color: '#a0a0b8',
    textDecoration: 'none',
    padding: '6px 14px',
    borderRadius: '6px',
    fontSize: '0.85rem',
    fontWeight: 500,
    transition: 'all 0.2s',
  },
  activeLink: {
    background: '#4361ee',
    color: 'white',
  },
  menuToggle: {
    display: 'none',
    background: 'none',
    border: 'none',
    color: '#e8e8e8',
    fontSize: '1.5rem',
    cursor: 'pointer',
  },
};

export default Navbar;
