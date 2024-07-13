import React, { useState } from 'react';
import './InputForm.css';

const InputForm = () => {
  const [formData, setFormData] = useState({
    longitude: '',
    latitude: '',
    minDistance: '',
    maxDistance: '',
    minAltitude: '',
    maxAltitude: '',
    date: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Send data to the Flask backend
    fetch('http://127.0.0.1:5000/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Success:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <div className="form-row">
        <label>
          Longitude:
          <input
            type="number"
            step="any"
            name="longitude"
            value={formData.longitude}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Latitude:
          <input
            type="number"
            step="any"
            name="latitude"
            value={formData.latitude}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Minimal Distance:
          <input
            type="number"
            step="any"
            name="minDistance"
            value={formData.minDistance}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Maximal Distance:
          <input
            type="number"
            step="any"
            name="maxDistance"
            value={formData.maxDistance}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Minimal Altitude:
          <input
            type="number"
            step="any"
            name="minAltitude"
            value={formData.minAltitude}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Maximal Altitude:
          <input
            type="number"
            step="any"
            name="maxAltitude"
            value={formData.maxAltitude}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Date:
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </label>
      </div>
      <button type="submit">Submit</button>
    </form>
  );
};

export default InputForm;
