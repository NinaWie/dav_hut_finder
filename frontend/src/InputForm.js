import React, { useState, useEffect } from 'react';
import { TextField, Button, Box, FormControlLabel, Checkbox } from '@mui/material';
import './InputForm.css';

const InputForm = ({ formData, setFormData, onSubmit }) => {
  const [localFormData, setLocalFormData] = useState(formData);
  const [filterByDate, setFilterByDate] = useState(false);  // New state for controlling the date filter

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

  const handleDateCheckboxChange = (e) => {
    const isChecked = e.target.checked;
    setFilterByDate(isChecked);

    setLocalFormData((prevData) => ({
      ...prevData,
      date: isChecked ? new Date().toISOString().split('T')[0] : ''
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSubmit = { ...localFormData };
    if (!filterByDate) {
      delete dataToSubmit.date; // Exclude date if unchecked
    }
    onSubmit(dataToSubmit, filterByDate);  // Send checkbox state to App.js
  };


  return (
    <form onSubmit={handleSubmit} className="input-form">
      <Box display="flex" flexDirection="row" flexWrap="nowrap" gap={2}>
        <TextField label="Longitude" type="number" step="any" name="longitude" value={localFormData.longitude} onChange={handleChange} required />
        <TextField label="Latitude" type="number" step="any" name="latitude" value={localFormData.latitude} onChange={handleChange} required />
        <TextField label="Minimal Distance" type="number" step="any" name="minDistance" value={localFormData.minDistance} onChange={handleChange} required />
        <TextField label="Maximal Distance" type="number" step="any" name="maxDistance" value={localFormData.maxDistance} onChange={handleChange} required />
        <TextField label="Minimal Altitude" type="number" step="any" name="minAltitude" value={localFormData.minAltitude} onChange={handleChange} required />
        <TextField label="Maximal Altitude" type="number" step="any" name="maxAltitude" value={localFormData.maxAltitude} onChange={handleChange} required />
      </Box>

      {/* New "Filter by Availability" Section */}
      <Box display="flex" flexDirection="column" gap={1} marginTop={2}>
        <FormControlLabel
          control={
            <Checkbox
              checked={filterByDate}
              onChange={handleDateCheckboxChange}
            />
          }
          label="Filter by Date"
        />

        {filterByDate && (
          <Box display="flex" flexDirection="row" flexWrap="nowrap" gap={2}>
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
            label="Required beds"
            type="number"
            name="minSpaces"
            value={localFormData.minSpaces}
            onChange={handleChange}
          />
          </Box>
        )}


      </Box>

      <Button type="submit" variant="contained" color="primary" style={{ marginTop: '10px' }}>
        Submit
      </Button>
    </form>
  );
};

export default InputForm;
