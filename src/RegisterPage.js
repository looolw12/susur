import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './RegisterPage.css';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleUsernameChange = (event) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event) => {
    setPassword(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await axios.post('http://localhost:8000/register', {
        username,
        password,
      });
      console.log(response.data); // Assuming the backend returns a success message
      navigate('/dashboard'); // Redirect to the dashboard page after successful registration
    } catch (error) {
      console.error(error); // Handle any errors that occur during the registration process
    }
  };

  return (
    <div className="register-page">
      <div className="left-background">
        <div className="content">
          <h2>Страница регистрации</h2>
          <form onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username">Имя пользователя:</label>
              <input type="text" id="username" value={username} onChange={handleUsernameChange} required />
            </div>
            <div>
              <label htmlFor="password">Пароль:</label>
              <input type="password" id="password" value={password} onChange={handlePasswordChange} required />
            </div>
            <button type="submit">Зарегистрироваться</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
