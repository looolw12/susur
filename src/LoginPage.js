import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import './LoginPage.css';
import logo from './logo.svg';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const handleEmailChange = (event) => {
    setEmail(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      // Send login request to the backend
      const response = await axios.post('http://localhost:8000/login', {
        username: email,
        password: password,
      });

      // Handle successful login
      console.log(response.data); // You can handle the response data according to your needs

      // Save the token to local storage
      localStorage.setItem('token', response.data.access_token);

      // Redirect the user to the categories page after successful login
      navigate('/categories');
    } catch (error) {
      // Handle error response
      if (error.response && error.response.status === 401) {
        setErrorMessage('Неверные учетные данные. Пожалуйста, попробуйте снова.');
      } else {
        setErrorMessage('Произошла ошибка при входе. Пожалуйста, попробуйте снова.');
      }
    }
  };

  return (
    <div className="login-page">
      <div className="left-background-login">
        <div className="logo-container-login">
          <Link to="/" className="link">
            <img src={logo} alt="Логотип" className="logo-login" />
            <h2>Multi-Tasker</h2>
          </Link>
        </div>
        <div className="content-login">
          <h3>Добро пожаловать!</h3>
          {errorMessage && <p className="error-message">{errorMessage}</p>}
          <form onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email">Email:</label>
              <input type="email" id="email" value={email} onChange={handleEmailChange} required />
            </div>
            <div>
              <label htmlFor="password">Пароль:</label>
              <input type="password" id="password" value={password} onChange={handlePasswordChange} required />
            </div>
            <button type="submit">Войти</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
