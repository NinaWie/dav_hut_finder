import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';  // Import hut emoji icon

function App() {
  const [coordinates, setCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [openWelcomeDialog, setOpenWelcomeDialog] = useState(true);  // Control for dialog state
  const [formData, setFormData] = useState({
    longitude: '10.72265625',
    latitude: '47.170598236405986',
    minDistance: '0',
    maxDistance: '100',
    minAltitude: '0',
    maxAltitude: '3000',
    date: "2024-09-08",//new Date().toISOString().split('T')[0],  // Default to today's date
    minSpaces: '1'
  });

  // Fetch markers when formData changes
  useEffect(() => {
    if (formData.longitude && formData.latitude) {
      fetchMarkers(formData);
    }
  }, [formData]);

  const fetchMarkers = (formData) => {
    // Ensure valid coordinates exist
    if (!formData.longitude || !formData.latitude) return;

    // Fetch markers based on formData
    fetch('http://127.0.0.1:5555/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setMarkers(data.markers);  // Update markers in the state
        }
      })
      .catch((error) => {
        console.error('Error fetching markers:', error);
      });
  };

  // Close the welcome dialog when the user clicks 'Got it'
  const handleCloseWelcomeDialog = () => {
    setOpenWelcomeDialog(false);
  };
  const handleFormSubmit = (newFormData) => {
    setFormData(newFormData);  // Trigger useEffect to fetch markers
  };

  const handleMapClick = (latlng) => {
    const newFormData = {
      ...formData,
      latitude: latlng.lat,
      longitude: latlng.lng,
    };
    setFormData(newFormData);  // Trigger marker update with new coordinates
  };

  return (
    <div className="App">
      <h1>Hut Finder</h1>
      <div className="content">
        {/* Pass current form data and markers */}
        <InputForm coordinates={coordinates} formData={formData} setFormData={setFormData} onSubmit={handleFormSubmit} />
        <MapComponent setCoordinates={setCoordinates} markers={markers} handleMapClick={handleMapClick} />
      </div>

      {/* Welcome Dialog */}
      <Dialog
        open={openWelcomeDialog}
        onClose={handleCloseWelcomeDialog}
      >
        <DialogTitle>Welcome to the Hut Finder <EmojiPeopleIcon fontSize="large" /></DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Please click somewhere on the map and submit afterwards to see which huts are available.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseWelcomeDialog} variant="contained" color="primary">
            Got it!
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App;
