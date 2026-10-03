import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';
import { Dialog, Box, DialogTitle, DialogContent, DialogActions, Button, Typography } from '@mui/material';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';
import InfoIcon from '@mui/icons-material/Info';

const getDefaultDates = () => {
  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  const toISODate = (date) => date.toISOString().split("T")[0]; // 'YYYY-MM-DD'

  return {
    startDate: toISODate(today),
    endDate: toISODate(tomorrow),
  };
};


function App() {
  const [coordinates, setCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [openWelcomeDialog, setOpenWelcomeDialog] = useState(true);
  const [filterByDate, setFilterByDate] = useState(false);
  const defaultDates = getDefaultDates();
  const [formData, setFormData] = useState({
    longitude: '10.72265625',
    latitude: '47.170598236405986',
    minDistance: '0',
    maxDistance: '250',
    minAltitude: '0',
    maxAltitude: '4000',
    date: defaultDates.startDate,
    minSpaces: '1',
    startDate: defaultDates.startDate,
    endDate: defaultDates.endDate,
    minHutDistance: 0,
    maxHutDistance: 13,
    useBeelineDistance: false,
    minAscent: 0,
    maxAscent: 3000
  });
  const [loading, setLoading] = useState(false);
  const [tabIndex, setTabIndex] = useState(0);
  const [openInfoDialog, setOpenInfoDialog] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };


  useEffect(() => {
    if (tabIndex === 0 && formData.longitude && formData.latitude) {
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

  const downloadRoutesAsCSV = () => {
    if (!routes || routes.length === 0) return;

    // Create CSV header
    const headers = ['Route #', 'Huts', 'Distance', 'Ascent/Descent'];
    const rows = routes.map((route, index) => [
      index + 1,
      route.infos,
      route.distance,
      route.ascent || 'N/A'
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `multi-day-routes-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="App">
      <div className="container">
        <InputForm
          coordinates={coordinates}
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleFormSubmit}
          filterByDate={filterByDate}
          loading={loading}
          tabIndex={tabIndex}
          handleTabChange={handleTabChange}
        />
        {routes.length > 0 && tabIndex === 1 && (
          <Box sx={{ p: 2, textAlign: 'center', display: 'flex', gap: 2, justifyContent: 'center', alignItems: 'center' }}>
            <Button 
              variant="contained" 
              color="success"
              onClick={downloadRoutesAsCSV}
            >
              Download Routes as CSV
            </Button>
            <Button
              variant="outlined"
              startIcon={<InfoIcon />}
              onClick={() => setOpenInfoDialog(true)}
              size="small"
            >
              Info
            </Button>
          </Box>
        )}
        <Box flex={1} display="flex">
          <MapComponent setCoordinates={setCoordinates} markers={markers} routes={routes} handleMapClick={handleMapClick} minSpaces={formData.minSpaces} radiusKm={Number(formData.maxDistance)}/>
        </Box>
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

      <Dialog open={openInfoDialog} onClose={() => setOpenInfoDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Multi-Day Route Planning - Info</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <Typography variant="body2">
              We filtered for huts within 20km beeline distance as candidate pairs for consecutive days of your hike.
            </Typography>
            <Typography variant="body2">
              We computed the distance between huts as the shortest distance in the graph of walking paths. Careful: this may contain glacier crossings or climbing paths that would require mountaineering skills!
            </Typography>
            <Typography variant="body2">
              Ascent and descent refer to the shortest-distance route using SRTM elevation data. Of course, there might be other longer routes with less ascent or descent depending on your preferences.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenInfoDialog(false)} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App;
