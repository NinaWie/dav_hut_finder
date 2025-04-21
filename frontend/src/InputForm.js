import React, { useState, useEffect } from 'react';
import { Slider, Typography, TextField, Button, Box, FormControlLabel, Checkbox } from '@mui/material';
import './InputForm.css';

const InputForm = ({ formData, setFormData, onSubmit }) => {
  const [localFormData, setLocalFormData] = useState(formData);
  const [filterByDate, setFilterByDate] = useState(false);  // New state for controlling the date filter

  useEffect(() => {
    setLocalFormData(formData);  // Sync local state with global form data
  }, [formData]);

  // Clamp endDate to always be ≥ startDate
  useEffect(() => {
    const { startDate, endDate } = localFormData;
    if (!startDate) return;

    // if endDate is empty OR before the new startDate → bump it up
    if (!endDate || endDate < startDate) {
      setLocalFormData(prev => ({
        ...prev,
        endDate: startDate,
      }));
    }
  }, [localFormData.startDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocalFormData((prevData) => ({
      ...prevData,
      [name]: value
    }));
  };
  const handleSliderChange = (event, newValue, name) => {
    const [min, max] = newValue; // Extract the min and max values from the range

    setLocalFormData((prevData) => ({
      ...prevData,
      minDistance: name === "distanceRange" ? min : prevData.minDistance,
      maxDistance: name === "distanceRange" ? max : prevData.maxDistance,
      minAltitude: name === "altitudeRange" ? min : prevData.minAltitude,
      maxAltitude: name === "altitudeRange" ? max : prevData.maxAltitude,
    }));
  };
  const handleSingleSliderChange = (event, newValue, name) => {
    const maxdist = newValue;

    setLocalFormData((prevData) => ({
      ...prevData,
      [name]: maxdist
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
    const submitter = e.nativeEvent.submitter;
    const action = submitter?.value;

    if (!filterByDate) {
      delete dataToSubmit.date; // Exclude date if unchecked
    }
    if (action === "applyFilters") {
      onSubmit(dataToSubmit, filterByDate, "applyFilters");
    } else if (action === "multiDay") {
      onSubmit(dataToSubmit, filterByDate, "multiDay");
    }
  };


  return (
    <form onSubmit={handleSubmit} className="input-form">
      <Box display="flex" flexDirection="row" gap={3} p={2}>

      <Box display="flex" flexDirection="column" gap={3} p={2}>
      <Typography variant="h6">Filter by Distance & Altitude</Typography>

        {/* Distance Range Slider */}
        <Box>
          <Typography gutterBottom>
            Distance from position: {localFormData.minDistance} km - {localFormData.maxDistance} km
          </Typography>
          <Slider
            value={[localFormData.minDistance, localFormData.maxDistance]}
            onChange={(e, value) => handleSliderChange(e, value, "distanceRange")}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value} km`}
            min={0}
            max={500} // Global max range for distance
            step={1}
          />

        {/* Altitude Range Slider */}
          <Typography gutterBottom>
            Altitude range: {localFormData.minAltitude} m - {localFormData.maxAltitude} m
          </Typography>
          <Slider
            value={[localFormData.minAltitude, localFormData.maxAltitude]}
            onChange={(e, value) => handleSliderChange(e, value, "altitudeRange")}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value} m`}
            min={0}
            max={4000} // Global max range for altitude
            step={10}
          />
          <Button type="submit" name="action" value="applyFilters" variant="contained" color="primary" style={{ marginTop: '10px' }}>
            Apply filters
          </Button>
        </Box>
      </Box>

      {/* Filter by Availability" Section */}
      <Box display="flex" flexDirection="column" gap={3} p={2}>
        <Typography variant="h6">Color by Availability</Typography>
        <FormControlLabel
          control={
            <Checkbox
              checked={filterByDate}
              onChange={handleDateCheckboxChange}
            />
          }
          label="Set Date"
        />
        {filterByDate && (
          <Box display="flex" flexDirection="row" flexWrap="nowrap" gap={2}>
          <TextField
            label="Date"
            type="date"
            name="date"
            value={localFormData.date}
            onChange={handleChange}
            InputLabelProps={{ shrink: true, }}
	    inputProps={{ min: localFormData.startDate || undefined }}
          />
          </Box>
        )}
        <Button type="submit" name="action" value="applyFilters" variant="contained" color="primary" style={{ marginTop: '10px' }}>
          Color by availability
        </Button>
      </Box>

      {/* Multi-day section */}
      <Box display="flex" flexDirection="column" gap={3} p={2}>
        <Typography variant="h6">Find multi-day hike</Typography>

        {/* Two-column layout */}
        <Box display="flex" flexDirection="row" gap={4} flexWrap="wrap">
          {/* Left column: Dates */}
          <Box display="flex" flexDirection="column" gap={2} flex={1}>
            <TextField
              label="Start Date"
              type="date"
              name="startDate"
              value={localFormData.startDate}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="End Date"
              type="date"
              name="endDate"
              value={localFormData.endDate}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
            />
          </Box>

          {/* Right column: Min spaces + distance slider */}
          <Box display="flex" flexDirection="column" gap={2} flex={1}>
            <TextField
              label="Minimal Spaces"
              type="number"
              name="minSpaces"
              value={localFormData.minSpaces}
              onChange={handleChange}
            />
            <Box display="flex" flexDirection="column" gap={0}>
              <Typography gutterBottom>
                Maximal distance between huts: 0 km - 13 km (beeline distance):
              </Typography>
              <Slider
                value={localFormData.maxHutDistance}
                onChange={(e, value) => handleSingleSliderChange(e, value, "maxHutDistance")}
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value} km`}
                min={0}
                max={13}
                step={1}
              />
            </Box>
          </Box>
        </Box>

        {/* Centered Button */}
        <Box display="flex" justifyContent="center" >
          <Button
            type="submit"
            name="action"
            value="multiDay"
            variant="contained"
            color="primary"
          >
            Find multi-day options
          </Button>
        </Box>
      </Box>
    </Box>
    </form>
  );
};

export default InputForm;
