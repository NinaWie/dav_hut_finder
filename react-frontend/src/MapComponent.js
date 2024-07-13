import React, { useState } from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const ClickableMap = ({ setCoordinates }) => {
  useMapEvents({
    click(e) {
      setCoordinates(e.latlng);
    },
  });

  return null;
};

const MapComponent = ({ setCoordinates }) => {
  return (
    <MapContainer center={[46.5, 10.5]} zoom={7} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <ClickableMap setCoordinates={setCoordinates} />
    </MapContainer>
  );
};

export default MapComponent;
