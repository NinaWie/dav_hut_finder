import React, { useState } from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';

function App() {
  const [coordinates, setCoordinates] = useState(null);

  return (
    <div className="App">
      <h1>DAV Hütten Finder</h1>
      <div className="content">
        <InputForm coordinates={coordinates} />
        <MapComponent setCoordinates={setCoordinates} />
      </div>
    </div>
  );
}

export default App;
