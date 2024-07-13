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

const ClickableMap = ({ setCoordinates, setMarkerPosition }) => {
  useMapEvents({
    click(e) {
      setCoordinates(e.latlng);
      setMarkerPosition(e.latlng);
    },
  });

  return null;
};

const MapComponent = ({ setCoordinates, markers }) => {
  const [markerPosition, setMarkerPosition] = useState(null);

  return (
    <MapContainer center={[46.5, 10.5]} zoom={8} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {markers.map((marker) => (
        <Marker key={marker.id} position={[marker.latitude, marker.longitude]}>
          <Popup>
            Hütte: {marker.name} 
            <br />
            Höhe: {marker.altitude}
            <br />
            Entfernung: {marker.distance} km
            <br />
            Verein: {marker.verein}
          </Popup>
        </Marker>
      ))}
      {markerPosition && <Marker position={markerPosition} />}
      <ClickableMap setCoordinates={setCoordinates} setMarkerPosition={setMarkerPosition} />
    </MapContainer>
  );
};

export default MapComponent;
