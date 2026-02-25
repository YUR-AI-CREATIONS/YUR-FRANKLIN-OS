import React, { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { FranklinIDE } from './components/FranklinIDE';
import './App.css';
import './LiquidGalaxy.css';

const PAGES = { LANDING: 'landing', IDE: 'ide' };

function App() {
  const [currentPage, setCurrentPage] = useState(PAGES.LANDING);
  
  const navigateToIDE = () => setCurrentPage(PAGES.IDE);
  const navigateToLanding = () => setCurrentPage(PAGES.LANDING);
  
  return (
    <div className="App">
      {currentPage === PAGES.LANDING && (
        <LandingPage onNavigateToIDE={navigateToIDE} />
      )}
      {currentPage === PAGES.IDE && (
        <FranklinIDE onBack={navigateToLanding} />
      )}
    </div>
  );
}

export default App;
