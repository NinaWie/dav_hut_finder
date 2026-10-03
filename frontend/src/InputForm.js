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
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { Collapse, FormControlLabel, Checkbox, Tooltip } from '@mui/material';


const InputForm = ({ formData, onSubmit, loading, tabIndex, handleTabChange}) => {
  const [localFormData, setLocalFormData] = useState(formData);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    setLocalFormData(formData);
  }, [formData]);

  useEffect(() => {
    const { startDate, endDate } = localFormData;
    if (startDate && (!endDate || endDate < startDate)) {
      setLocalFormData(prev => ({ ...prev, endDate: startDate }));
    }
  }, [localFormData.startDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocalFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSliderChange = (e, newValue, name) => {
    const [min, max] = newValue;
    setLocalFormData(prev => ({
      ...prev,
      ...(name === 'distanceRange' ? { minDistance: min, maxDistance: max } : {}),
      ...(name === 'altitudeRange' ? { minAltitude: min, maxAltitude: max } : {}),
      ...(name === 'hutDistanceRange' ? { minHutDistance: min, maxHutDistance: max } : {}),
      ...(name === 'ascentRange' ? { minAscent: min, maxAscent: max } : {})
    }));
  };

  const maxHutDistanceLimit = localFormData.useBeelineDistance ? 20 : 40;

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setLocalFormData(prev => {
      const next = { ...prev, [name]: checked };
      if (name === 'useBeelineDistance') {
        const limit = checked ? 20 : 40;
        next.minHutDistance = Math.min(Number(prev.minHutDistance), limit);
        next.maxHutDistance = Math.min(Number(prev.maxHutDistance), limit);
      }
      return next;
    });
  };

  const handleSubmit = (e) => {
    if (!isDateRangeValid()) {
      // Optionally show an alert/snackbar
      return;
    }
    e.preventDefault();
    const dataToSubmit = { ...localFormData };
    if (!dataToSubmit.date) delete dataToSubmit.date;
    const action = e.nativeEvent.submitter?.value;
    const filterByDate = Boolean(dataToSubmit.date);
    onSubmit(dataToSubmit, filterByDate, action === 'multiDay' ? 'multiDay' : 'applyFilters');
  };

  const isDateRangeValid = () => {
    const { startDate, endDate } = localFormData;

    if (!startDate || !endDate) return false;

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start) || isNaN(end)) return false;

    // At least one day apart
    return start < end;
  };

  const showError = localFormData.startDate && localFormData.endDate && !isDateRangeValid();


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
      {/* Tab header row with arrow button */}
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        width="100%"
        mb={1}
  >      <Tabs
        value={tabIndex}
        onChange={handleTabChange}
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
      <Button
        onClick={() => setExpanded(prev => !prev)}
        sx={{
          minWidth: 0,
          ml: 1,
          p: 0.5,
          alignSelf: 'center'
        }}
      >
        {expanded ? <ExpandLess /> : <ExpandMore />}
      </Button>
    </Box>
      <Collapse in={expanded} timeout="auto" unmountOnExit>

        {/* Single-Day Tab */}
        {tabIndex === 0 && (
          <Box width="100%" display="flex" justifyContent="center" p={isMobile ? 1 : 2}>
            <Box width="100%" maxWidth={isMobile ? '90%' : 600}>
              <Typography gutterBottom align="center">
                Distance from position: {localFormData.minDistance} km - {localFormData.maxDistance} km
              </Typography>
              <Slider
                value={[localFormData.minDistance, localFormData.maxDistance]}
                onChange={(e, v) => handleSliderChange(e, v, 'distanceRange')}
                valueLabelDisplay="auto"
                min={0}
                max={500}
              />
              <Typography gutterBottom align="center">
                Hut altitude: {localFormData.minAltitude} m - {localFormData.maxAltitude} m
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
            <Box
              width="100%"
              maxWidth={isMobile ? '90%' : 900}
              display="flex"
              flexDirection={{ xs: 'column', sm: 'row' }}
              gap={isMobile ? 1 : 4}
            >
              <Box flex={1} display="flex" flexDirection="column" gap={2}>
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
                <TextField
                  fullWidth
                  label="End Date"
                  type="date"
                  name="endDate"
                  value={localFormData.endDate}
                  onChange={handleChange}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                  error={showError}
                  helperText={showError ? "Start date must be before end date" : ""}
                />
                <TextField
                  fullWidth
                  label="Minimal Spaces"
                  type="number"
                  name="minSpaces"
                  value={localFormData.minSpaces}
                  onChange={handleChange}
                  size="small"
                />
                <Box textAlign="center">
                  <Tooltip title="Off by default: routes only use pairs of huts with an actual mapped hiking trail between them. Tick this to allow straight-line (beeline) distance instead, e.g. for routes crossing a glacier with no marked trail.">
                    <FormControlLabel
                      control={
                        <Checkbox
                          name="useBeelineDistance"
                          checked={Boolean(localFormData.useBeelineDistance)}
                          onChange={handleCheckboxChange}
                          size="small"
                        />
                      }
                      label="Use beeline distance"
                    />
                  </Tooltip>
                </Box>
                <Box textAlign="center">
                  <Button
                    type="submit"
                    value="multiDay"
                    variant="contained"
                    disabled={!isDateRangeValid() || loading}
                    startIcon={loading ? <CircularProgress size={isMobile ? 16 : 20} /> : null}
                    size="small"
                  >
                    Find Multi-Day Options
                  </Button>
                </Box>
              </Box>
              <Box flex={1}>
                <Typography align="center" variant="body2">
                  Distance from position: {localFormData.minDistance} km - {localFormData.maxDistance} km
                </Typography>
                <Slider
                  value={[localFormData.minDistance, localFormData.maxDistance]}
                  onChange={(e, v) => handleSliderChange(e, v, 'distanceRange')}
                  valueLabelDisplay="auto"
                  size="small"
                  min={0}
                  max={500}
                />
                <Typography align="center" variant="body2">
                  Hut altitude: {localFormData.minAltitude} m - {localFormData.maxAltitude} m
                </Typography>
                <Slider
                  value={[localFormData.minAltitude, localFormData.maxAltitude]}
                  onChange={(e, v) => handleSliderChange(e, v, 'altitudeRange')}
                  valueLabelDisplay="auto"
                  size="small"
                  min={0}
                  max={4000}
                  step={10}
                />
                <Typography align="center" variant="body2">
                  Distance between huts: {localFormData.minHutDistance} km - {localFormData.maxHutDistance} km
                </Typography>
                <Slider
                  value={[Number(localFormData.minHutDistance), Number(localFormData.maxHutDistance)]}
                  onChange={(e, v) => handleSliderChange(e, v, 'hutDistanceRange')}
                  valueLabelDisplay="auto"
                  size="small"
                  min={0}
                  max={maxHutDistanceLimit}
                  step={1}
                />
                {!localFormData.useBeelineDistance && (
                  <>
                    <Typography align="center" variant="body2">
                      Ascent between huts: {localFormData.minAscent} m - {localFormData.maxAscent} m
                    </Typography>
                    <Slider
                      value={[localFormData.minAscent, localFormData.maxAscent]}
                      onChange={(e, v) => handleSliderChange(e, v, 'ascentRange')}
                      valueLabelDisplay="auto"
                      size="small"
                      min={0}
                      max={3000}
                      step={50}
                    />
                  </>
                )}
              </Box>
            </Box>
          </Box>
        )}
      </Collapse>
    </Box>
  );
};

export default InputForm;
