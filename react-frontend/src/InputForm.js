import React, { useState, useEffect } from 'react';
import { TextField, Button, Box } from '@mui/material';
import './InputForm.css';

const InputForm = ({ formData, setFormData, onSubmit }) => {
  const [localFormData, setLocalFormData] = useState(formData);

  useEffect(() => {
    setLocalFormData(formData);  // Sync local state with global form data
  }, [formData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocalFormData((prevData) => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Submit the local form data to App.js
    onSubmit(localFormData);
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <Box display="flex" flexDirection="row" flexWrap="nowrap" gap={2}>
        <TextField
          label="Longitude"
          type="number"
          step="any"
          name="longitude"
          value={localFormData.longitude}
          onChange={handleChange}
          required
        />
        <TextField
          label="Latitude"
          type="number"
          step="any"
          name="latitude"
          value={localFormData.latitude}
          onChange={handleChange}
          required
        />
        <TextField
          label="Minimal Distance"
          type="number"
          step="any"
          name="minDistance"
          value={localFormData.minDistance}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Maximal Distance"
          type="number"
          step="any"
          name="maxDistance"
          value={localFormData.maxDistance}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Minimal Altitude"
          type="number"
          step="any"
          name="minAltitude"
          value={localFormData.minAltitude}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Maximal Altitude"
          type="number"
          step="any"
          name="maxAltitude"
          value={localFormData.maxAltitude}
          onChange={handleChange}
          required
          inputProps={{ min: 0 }}
        />
        <TextField
          label="Date"
          type="date"
          name="date"
          value={localFormData.date}
          onChange={handleChange}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          label="Minimal Spaces"
          type="number"
          name="minSpaces"
          value={localFormData.minSpaces}
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
