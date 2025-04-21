import React, { useState, useEffect } from 'react';
import {
  Slider,
  Typography,
  TextField,
  Button,
  Box,
  Tabs,
  Tab,
  CircularProgress,
  useMediaQuery,
  useTheme
} from '@mui/material';
import './InputForm.css';

const InputForm = ({ formData, onSubmit, loading }) => {
  const [localFormData, setLocalFormData] = useState(formData);
  const [tabIndex, setTabIndex] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    setLocalFormData(formData);
  }, [formData]);

  useEffect(() => {
    const { startDate, endDate } = localFormData;
    if (startDate && (!endDate || endDate < startDate)) {
      setLocalFormData(prev => ({ ...prev, endDate: startDate }));
    }
  }, [localFormData.startDate]);

  const handleTabChange = (_, newIndex) => setTabIndex(newIndex);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocalFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSliderChange = (e, newValue, name) => {
    const [min, max] = newValue;
    setLocalFormData(prev => ({
      ...prev,
      ...(name === 'distanceRange' ? { minDistance: min, maxDistance: max } : {}),
      ...(name === 'altitudeRange' ? { minAltitude: min, maxAltitude: max } : {})
    }));
  };

  const handleSingleSliderChange = (_, newValue, name) => {
    setLocalFormData(prev => ({ ...prev, [name]: newValue }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const dataToSubmit = { ...localFormData };
    if (!dataToSubmit.date) delete dataToSubmit.date;
    const action = e.nativeEvent.submitter?.value;
    const filterByDate = Boolean(dataToSubmit.date);
    onSubmit(dataToSubmit, filterByDate, action === 'multiDay' ? 'multiDay' : 'applyFilters');
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      width={isMobile ? '95%' : '100%'}
      display="flex"
      flexDirection="column"
      alignItems="center"
      p={isMobile ? 1 : 2}
      sx={{ fontSize: isMobile ? '0.875rem' : '1rem' }}
    >
      <Tabs
        value={tabIndex}
        onChange={handleTabChange}
        centered
        textColor="primary"
        indicatorColor="primary"
        sx={{
          bgcolor: 'background.paper',
          minHeight: isMobile ? 32 : 48
        }}
      >
        <Tab label="Single-Day" sx={{ minWidth: isMobile ? 80 : 120 }} />
        <Tab label="Multi-Day" sx={{ minWidth: isMobile ? 80 : 120 }} />
      </Tabs>

      {/* Single-Day Tab */}
      {tabIndex === 0 && (
        <Box width="100%" display="flex" justifyContent="center" p={isMobile ? 1 : 2}>
          <Box width="100%" maxWidth={isMobile ? 360 : 600}>
            <Typography gutterBottom align="center">
              Distance: {localFormData.minDistance} km - {localFormData.maxDistance} km
            </Typography>
            <Slider
              value={[localFormData.minDistance, localFormData.maxDistance]}
              onChange={(e, v) => handleSliderChange(e, v, 'distanceRange')}
              valueLabelDisplay="auto"
              min={0}
              max={500}
            />
            <Typography gutterBottom align="center">
              Altitude: {localFormData.minAltitude} m - {localFormData.maxAltitude} m
            </Typography>
            <Slider
              value={[localFormData.minAltitude, localFormData.maxAltitude]}
              onChange={(e, v) => handleSliderChange(e, v, 'altitudeRange')}
              valueLabelDisplay="auto"
              min={0}
              max={4000}
              step={10}
            />
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mt={2}>
              <TextField
                fullWidth
                label="Minimal Spaces"
                type="number"
                name="minSpaces"
                value={localFormData.minSpaces}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
              <TextField
                fullWidth
                label="Date"
                type="date"
                name="date"
                value={localFormData.date}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Box>
            <Box textAlign="center" mt={2}>
              <Button
                type="submit"
                value="applyFilters"
                variant="contained"
                size={isMobile ? 'small' : 'medium'}
              >
                Apply Filters
              </Button>
            </Box>
          </Box>
        </Box>
      )}

      {/* Multi-Day Tab */}
      {tabIndex === 1 && (
        <Box width="100%" display="flex" justifyContent="center" p={isMobile ? 1 : 2}>
          <Box width="100%" maxWidth={isMobile ? '90%' : 600}>
            <Typography gutterBottom align="center">
              Distance: {localFormData.minDistance} km - {localFormData.maxDistance} km
            </Typography>
            <Slider
              value={[localFormData.minDistance, localFormData.maxDistance]}
              onChange={(e, v) => handleSliderChange(e, v, 'distanceRange')}
              valueLabelDisplay="auto"
              min={0}
              max={500}
            />
            <Typography gutterBottom align="center">
              Altitude: {localFormData.minAltitude} m - {localFormData.maxAltitude} m
            </Typography>
            <Slider
              value={[localFormData.minAltitude, localFormData.maxAltitude]}
              onChange={(e, v) => handleSliderChange(e, v, 'altitudeRange')}
              valueLabelDisplay="auto"
              min={0}
              max={4000}
              step={10}
            />
            <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} gap={2} mt={2}>
              <Box flex={1}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  name="startDate"
                  value={localFormData.startDate}
                  onChange={handleChange}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                />
                <Box mt={2}>
                  <TextField
                    fullWidth
                    label="End Date"
                    type="date"
                    name="endDate"
                    value={localFormData.endDate}
                    onChange={handleChange}
                    InputLabelProps={{ shrink: true }}
                    size="small"
                  />
                </Box>
              </Box>
              <Box flex={1}>
                <TextField
                  fullWidth
                  label="Minimal Spaces"
                  type="number"
                  name="minSpaces"
                  value={localFormData.minSpaces}
                  onChange={handleChange}
                  size="small"
                />
                <Box mt={4}>
                  <Typography gutterBottom align="center">
                    Max distance between huts: {localFormData.maxHutDistance} km
                  </Typography>
                  <Slider
                    value={localFormData.maxHutDistance}
                    onChange={(e, v) => handleSingleSliderChange(e, v, 'maxHutDistance')}
                    valueLabelDisplay="auto"
                    min={0}
                    max={13}
                    step={1}
                  />
                </Box>
              </Box>
            </Box>
            <Box textAlign="center" mt={2}>
              <Button
                type="submit"
                value="multiDay"
                variant="contained"
                disabled={loading}
                startIcon={<CircularProgress size={isMobile ? 16 : 20} />}
                size="small"
              >
                Find Multi-Day Options
              </Button>
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default InputForm;

