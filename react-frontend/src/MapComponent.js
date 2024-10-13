import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
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

// Custom icon for the clicked marker (personIcon)
const personIcon = new L.Icon({
  iconUrl: '/hiking.png',  // Replace with your image URL or static file path
  iconSize: [38, 38],  // Size of the icon
  iconAnchor: [19, 38],  // Point of the icon which will correspond to marker's location
  popupAnchor: [0, -38],  // Point from which the popup should open relative to the iconAnchor
});

const ClickableMap = ({ handleMapClick }) => {
  useMapEvents({
    click(e) {
      handleMapClick(e.latlng);  // Trigger marker update on click
    },
  });

  return null;
};

const MapComponent = ({ markers, handleMapClick }) => {
  const [markerPosition, setMarkerPosition] = useState(null);

  return (
    <MapContainer center={[46.5, 10.5]} zoom={8} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {/* Render markers from the fetched data */}
      {markers.map((marker) => (
        <Marker key={marker.id} position={[marker.latitude, marker.longitude]}>
          <Popup>
            Hütte: {marker.name}
            <br />
            Höhe: {marker.altitude} meters
            <br />
            Entfernung: {marker.distance} km
            <br />
            Verein: {marker.verein}
          </Popup>
        </Marker>
      ))}

      {/* Render the personIcon at the clicked position */}
      {markerPosition && (
        <Marker position={markerPosition} icon={personIcon}>
          <Popup>
            <div>
              <strong>Your selected location:</strong><br />
              <strong>Latitude:</strong> {markerPosition.lat}<br />
              <strong>Longitude:</strong> {markerPosition.lng}
            </div>
          </Popup>
        </Marker>
      )}

      {/* Update marker position and handle click event */}
      <ClickableMap
        handleMapClick={(latlng) => {
          setMarkerPosition(latlng);  // Set the position of the clicked marker
          handleMapClick(latlng);  // Trigger marker update for coordinates
        }}
      />
    </MapContainer>
  );
};

export default MapComponent;
