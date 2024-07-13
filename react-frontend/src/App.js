import React from 'react';
import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';

function App() {
  return (
    <div className="App">
      <h1>React Leaflet Map with Input Form</h1>
      <InputForm />
      <MapComponent />
    </div>
  );
}

export default App;
