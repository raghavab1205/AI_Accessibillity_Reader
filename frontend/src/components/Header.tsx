import '../styles/Header.css';

const Header = () => {
  return (
    <header className="app-header">
      <div className="logo-container">
        <div className="logo-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
        <h1>AI Accessibility Reader</h1>
      </div>
      
      <div className="header-tagline">
        <p>Making text accessible through speech</p>
        <div className="sdg-badge">
          <span>SDG 10</span>
          <span className="tooltip">Sustainable Development Goal 10: Reduced Inequalities</span>
        </div>
      </div>
    </header>
  );
};

export default Header;