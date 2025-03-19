import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';

function App() {
  const [coordinates, setCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [openWelcomeDialog, setOpenWelcomeDialog] = useState(true);
  const [filterByDate, setFilterByDate] = useState(false);
  const [formData, setFormData] = useState({
    longitude: '10.72265625',
    latitude: '47.170598236405986',
    minDistance: '0',
    maxDistance: '500',
    minAltitude: '0',
    maxAltitude: '5000',
    date: '',
    minSpaces: '1'
  });

  useEffect(() => {
    if (formData.longitude && formData.latitude) {
      fetchMarkers({ ...formData, filterByDate });
    }
  }, [formData]);

  const fetchMarkers = (formData) => {
    if (!formData.longitude || !formData.latitude) return;

    // Prepare data for submission
    const dataToSubmit = { ...formData };
    if (!filterByDate) {
      delete dataToSubmit.date; // Only exclude date if checkbox is unchecked
    }

    fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dataToSubmit)
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setMarkers(data.markers);
        }
      })
      .catch((error) => {
        console.error('Error fetching markers:', error);
      });
  };

  const handleCloseWelcomeDialog = () => {
    setOpenWelcomeDialog(false);
  };

  const handleFormSubmit = (newFormData, newFilterByDate) => {
    setFormData(newFormData);
    setFilterByDate(newFilterByDate);  // Track checkbox state
  };

  const handleMapClick = (latlng) => {
    const newFormData = {
      ...formData,
      latitude: latlng.lat,
      longitude: latlng.lng,
    };

    if (!filterByDate) {
      delete newFormData.date;
    }

    setFormData(newFormData);
  };

  return (
    <div className="App">
      <h1>Hut Finder</h1>
      <div className="content">
        <InputForm
          coordinates={coordinates}
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleFormSubmit}
          filterByDate={filterByDate} // NEW: Pass checkbox state
        />
        <MapComponent setCoordinates={setCoordinates} markers={markers} handleMapClick={handleMapClick} minSpaces={formData.minSpaces} />
      </div>

      <Dialog open={openWelcomeDialog} onClose={handleCloseWelcomeDialog}>
        <DialogTitle>Welcome to the Hut Finder <EmojiPeopleIcon fontSize="large" /></DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Please click somewhere on the map. Optionally filter by date and hit submit to see which huts are available by date.
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
