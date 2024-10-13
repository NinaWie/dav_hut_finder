import React, { useState, useEffect } from 'react';
import { TextField, Button, Box } from '@mui/material';
import './InputForm.css';

const InputForm = ({ coordinates, setMarkers }) => {
  const [formData, setFormData] = useState({
    longitude: '',
    latitude: '',
    minDistance: '0',
    maxDistance: '1000',
    minAltitude: '0',
    maxAltitude: '3000',
    date: '2024-07-31',
    minSpaces: '1'
  });

  useEffect(() => {
    if (coordinates) {
      setFormData((prevData) => ({
        ...prevData,
        latitude: coordinates.lat,
        longitude: coordinates.lng,
      }));
    }
  }, [coordinates]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Ensure all positive number fields are positive
    if (
      parseFloat(formData.minDistance) < 0 ||
      parseFloat(formData.maxDistance) < 0 ||
      parseFloat(formData.minAltitude) < 0 ||
      parseFloat(formData.maxAltitude) < 0
    ) {
      alert('Distance and altitude values must be positive numbers.');
      return;
    }

    // Send data to the Flask backend
    fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setMarkers(data.markers);
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <Box display="flex" flexDirection="row" flexWrap="nowrap" gap={2}>
        <TextField
          label="Longitude"
          type="number"
          step="any"
          name="longitude"
          value={formData.longitude}
          onChange={handleChange}
          required
        />
        <TextField
          label="Latitude"
          type="number"
          step="any"
          name="latitude"
          value={formData.latitude}
          onChange={handleChange}
          required
        />
        <TextField
          label="Minimal Distance"
          type="number"
          step="any"
          name="minDistance"
          value={formData.minDistance}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Maximal Distance"
          type="number"
          step="any"
          name="maxDistance"
          value={formData.maxDistance}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Minimal Altitude"
          type="number"
          step="any"
          name="minAltitude"
          value={formData.minAltitude}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Maximal Altitude"
          type="number"
          step="any"
          name="maxAltitude"
          value={formData.maxAltitude}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Date"
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="Minimal Spaces"
          type="number"
          name="minSpaces"
          value={formData.minSpaces}
          onChange={handleChange}
        />
      </Box>
      <Button type="submit" variant="contained" color="primary" style={{ marginTop: '10px' }}>
        Submit
      </Button>
    </form>
  );
};

export default InputForm;
