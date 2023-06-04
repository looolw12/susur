import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import StartPage from './StartPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import AuthenticatedPage from './AuthenticatedPage';
import './App.css';

class App extends React.Component {
  render() {
    return (
      <Router>
        <div>
          <Routes>
            <Route path="/" element={<StartPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/authenticated" element={<AuthenticatedPage />} />
          </Routes>
        </div>
      </Router>
    );
  }
}

export default App;
