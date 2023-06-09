import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CategoryPage = () => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    getCategories();
  }, []);

  const getCategories = () => {
    axios
      .get('http://localhost:8000/categories', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })
      .then((response) => {
        setCategories(response.data.categories);
      })
      .catch((error) => {
        console.error('Error:', error);
        // Добавьте код для обработки ошибок
      });
  };

  const handleNameChange = (event) => {
    setName(event.target.value);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    axios
      .post(
        'http://localhost:8000/categories',
        { name, description },
        {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      )
      .then((response) => {
        console.log(response.data);
        // Добавьте код для обработки успешного создания категории
        getCategories();
        setName('');
        setDescription('');
      })
      .catch((error) => {
        console.error('Error:', error);
        // Добавьте код для обработки ошибок
      });
  };

  const handleDelete = (categoryId) => {
    axios
      .delete(`http://localhost:8000/categories/${categoryId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })
      .then((response) => {
        console.log(response.data);
        // Добавьте код для обработки успешного удаления категории
        getCategories();
      })
      .catch((error) => {
        console.error('Error:', error);
        // Добавьте код для обработки ошибок
      });
  };

  return (
    <div style={{ backgroundColor: 'white' }}>
      <h2>Create Category</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Name:
          <input type="text" value={name} onChange={handleNameChange} />
        </label>
        <br />
        <label>
          Description:
          <textarea value={description} onChange={handleDescriptionChange} />
        </label>
        <br />
        <input type="submit" value="Create" />
      </form>
      <h2>Categories</h2>
      <ul>
        {categories.map((category) => (
          <li key={category.id}>
            <h3>{category.name}</h3>
            <p>{category.description}</p>
            <button onClick={() => handleDelete(category.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CategoryPage;
