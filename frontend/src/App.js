import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';

function App() {
  const [coordinates, setCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [openWelcomeDialog, setOpenWelcomeDialog] = useState(true);
  const [filterByDate, setFilterByDate] = useState(false);
  const [formData, setFormData] = useState({
    longitude: '10.72265625',
    latitude: '47.170598236405986',
    minDistance: '0',
    maxDistance: '250',
    minAltitude: '0',
    maxAltitude: '4000',
    date: '',
    minSpaces: '1',
    startDate: '',
    endDate: '',
    maxHutDistance: 13
  });
  const [loading, setLoading] = useState(false);

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
          // NOTE: clear polylines? setRoutes([]);
        }
      })
      .catch((error) => {
        console.error('Error fetching markers:', error);
      });
  };

  const fetchMultiDayMarkers = (formData) => {
    setLoading(true);

    fetch('/api/multi_day', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setRoutes(data.routes);
          setMarkers(data.markers);
        }
      })
      .catch((error) => {
        console.error('Error fetching multi-day markers:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleCloseWelcomeDialog = () => {
    setOpenWelcomeDialog(false);
  };

  const handleFormSubmit = (newFormData, newFilterByDate, actionType) => {
    if (actionType === 'multiDay') {
      fetchMultiDayMarkers(newFormData);
    } else {
      setFormData(newFormData);
      setFilterByDate(newFilterByDate); // Will trigger useEffect → fetchMarkers
      setRoutes([]);
    }
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
      <div className="content">
        <InputForm
          coordinates={coordinates}
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleFormSubmit}
          filterByDate={filterByDate}
          loading={loading}
        />
        <MapComponent setCoordinates={setCoordinates} markers={markers} routes={routes} handleMapClick={handleMapClick} minSpaces={formData.minSpaces} radiusKm={Number(formData.maxDistance)}/>
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
