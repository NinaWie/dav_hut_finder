import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for missing default icon issue in Leaflet
let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow
});

L.Marker.prototype.options.icon = DefaultIcon;

const MapComponent = () => {
  const [markers, setMarkers] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/markers')
      .then(response => response.json())
      .then(data => setMarkers(data))
      .catch(error => console.error('Error fetching markers:', error));
  }, []);

  return (
    <MapContainer center={[46.5, 10.5]} zoom={7} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {markers.map(marker => (
        <Marker key={marker.id} position={marker.position}>
          <Popup>Hütte: { marker.name} </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapComponent;
