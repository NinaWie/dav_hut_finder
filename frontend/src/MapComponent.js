import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
// Fix Leaflet marker icons not displaying correctly in React apps
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

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

const getMarkerColor = (placesAvail, minSpaces) => {
  minSpaces = minSpaces;
  if (placesAvail < 0) return 'grey';         // No data or unknown availability
  if (placesAvail >= minSpaces + 5) return 'green';   // Plenty of spaces
  if (placesAvail >= minSpaces) return 'orange';   // Limited availability
  if (placesAvail < minSpaces) return 'red';       // full
  return 'blue';                        // Fully booked or unavailable
};

const createCustomMarker = (color) => {
  return new L.Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${color}.png`,
      iconSize: [25, 41],  // Default Leaflet marker size
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowUrl: markerShadow,
      shadowSize: [41, 41]
  });
};


const MapComponent = ({ markers, routes, handleMapClick, minSpaces, radiusKm }) => {
  // Set default position for the personIcon on map load
  const [markerPosition, setMarkerPosition] = useState({
    lat: 47.170598236405986,
    lng: 10.72265625,
  });

  return (
    <MapContainer center={[46.5, 10.5]} zoom={8} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {markers.map((marker) => {
          const markerColor = getMarkerColor(marker.places_avail, minSpaces);  // Define color logic
          const customIcon = createCustomMarker(markerColor);

          return (
              <Marker
                  key={marker.id}
                  position={[marker.latitude, marker.longitude]}
                  icon={customIcon}  // Use custom pin-style icon
              >
                  <Popup>
                      Hütte: {marker.name}
                      <br />
                      Höhe: {marker.altitude} meters
                      <br />
                      Entfernung: {marker.distance} km
                      <br />
                      Verein: {marker.verein}
                      {marker.places_avail !== undefined && (
                          <>
                              <br />
                              Available Beds: {marker.places_avail < 0 ? 'N/A' : marker.places_avail}
                          </>
                      )}
                      {marker.link && (
                          <>
                              <br />
                              <a
                                  href={marker.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{ color: 'blue', textDecoration: 'underline' }}
                              >
                                  Book here
                              </a>
                          </>
                      )}

                  </Popup>
              </Marker>
          );
      })}

      {/* draw the search-radius circle */}
      {markerPosition && radiusKm > 0 && (
        <Circle
          center={markerPosition}
          radius={radiusKm * 1000}       // conversions to meters
          pathOptions={{
            color: '#3388ff',
            weight: 2,
            opacity: 0.5,
            fillOpacity: 0.1,
          }}
        />
      )}

      {routes.map((route, index) => (
        <Polyline
          key={index}
          positions={route.coordinates}
          color="purple"
          weight={4}
          opacity={0.8}
          eventHandlers={{
            mouseover: (e) => {
              const layer = e.target;
              layer.setStyle({ color: 'orange' });
              layer.bindPopup(`<b>${route.infos}</b>`).openPopup();
            },
            mouseout: (e) => {
              const layer = e.target;
              layer.setStyle({ color: 'purple' });
              layer.closePopup();
            },
          }}
        />
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
