import React, { Component } from 'react';
import { Link, Navigate } from 'react-router-dom';
import logo from './logo.svg';
import { ReactComponent as LoginIcon } from './login.svg';
import { ReactComponent as RegisterIcon } from './register.svg';
import './App.css';


class StartPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isAuthenticated: false,
    };
  }

  handleLogin = () => {
    this.setState({ isAuthenticated: true });
  };

  render() {
    const { isAuthenticated } = this.state;

    return (
      <div>
        <header>
            <div className="logo-container">
              <img src={logo} alt="Логотип компании" className="logo" />
              <h1>Мое приложение</h1>
            </div>
            <div className="buttons-container">
              {isAuthenticated ? (
                <Navigate to="/login" replace />
              ) : (
                <Link to="/login" className="action-button" onClick={this.handleLogin}>
                  <LoginIcon className="button-icon" />
                </Link>
              )}
              <Link to="/register" className="action-button">
                <RegisterIcon className="button-icon" />
              </Link>
            </div>
          </header>
          <div className='start-screen'>
              <h1>“Самый удобный” инструмент для отслеживания ваших задач</h1>
              <div className="subtext">
                <p>Здесь вы сможете отслеживать свои задачи, а также назначать их коллегам и друзьям, и совместно трудиться над проектом.</p>
              </div>
            </div>
      </div>
    );
  }
}

export default StartPage;