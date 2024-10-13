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

  useEffect(() => {
    // Fetch initial markers
    fetch('http://127.0.0.1:5555/api/markers')
      .then((response) => response.json())
      .then((data) => {
        if (data.status === 'success') {
          setMarkers(data.markers);
        }
      })
      .catch((error) => {
        console.error('Error fetching markers:', error);
      });
  }, []);

  // Close the welcome dialog when the user clicks 'Got it'
  const handleCloseWelcomeDialog = () => {
    setOpenWelcomeDialog(false);
  };

  return (
    <div className="App">
      <h1>DAV Hütten Finder</h1>
      <div className="content">
        <InputForm coordinates={coordinates} setMarkers={setMarkers} />
        <MapComponent setCoordinates={setCoordinates} markers={markers} />
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
