import React, { useState, useEffect } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';

function App() {
  const [coordinates, setCoordinates] = useState(null);
  const [markers, setMarkers] = useState([]);

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

  return (
    <div className="App">
      <h1>DAV Hütten Finder</h1>
      <div className="content">
        <InputForm coordinates={coordinates} setMarkers={setMarkers} />
        <MapComponent setCoordinates={setCoordinates} markers={markers} />
      </div>
    </div>
  );
}

export default App;
