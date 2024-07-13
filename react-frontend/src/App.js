import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

import './App.css';
import MapComponent from './MapComponent';
import InputForm from './InputForm';

function App() {
  return (
    <div className="App">
      <h1>DAV Hütten Finder</h1>
      <InputForm />
      <MapComponent />
    </div>
  );
}

export default App;
