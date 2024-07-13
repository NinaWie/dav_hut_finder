import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, Popup } from 'react-leaflet';
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

const ClickableMap = ({ setCoordinates, setMarkerPosition }) => {
  useMapEvents({
    click(e) {
      setCoordinates(e.latlng);
      setMarkerPosition(e.latlng);
    },
  });

  return null;
};

const MapComponent = ({ setCoordinates }) => {
  const [markerPosition, setMarkerPosition] = useState(null);
  const [markers, setMarkers] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/markers')
      .then((response) => response.json())
      .then((data) => setMarkers(data))
      .catch((error) => console.error('Error fetching markers:', error));
  }, []);

  return (
    <MapContainer center={[46.5, 10.5]} zoom={8} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {markers.map((marker) => (
        <Marker key={marker.id} position={marker.position}>
          <Popup>{marker.name}</Popup>
        </Marker>
      ))}
      {markerPosition && <Marker position={markerPosition} />}
      <ClickableMap setCoordinates={setCoordinates} setMarkerPosition={setMarkerPosition} />
    </MapContainer>
  );
};

export default MapComponent;
