import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function MapView() {
  const [startName, setStartName] = useState("");
  const [endName, setEndName] = useState("");
  const [route, setRoute] = useState([]);
  const [error, setError] = useState("");

  const handleRoute = async () => {
  setError("");
  if (!startName || !endName) {
    setError("Please enter both start and end locations.");
    return;
  }
  try {
    const res = await fetch("http://127.0.0.1:5000/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ start: startName, end: endName }),
    });
    const data = await res.json();
    if (res.ok && data.route) {
      console.log("Route for Polyline:", data.route); // Add this line!
      setRoute(data.route);
    } else {
      setError(data.error || "Routing failed");
      setRoute([]);
    }
  } catch (err) {
    setError("Error fetching route");
    console.error(err);
    setRoute([]);
  }
};


  const center = route.length > 0 ? route[0] : [12.9716, 77.5946]; // Default Bangalore center

  return (
    <div>
      <h2>Map View with Routing</h2>
      <div style={{ marginBottom: "10px" }}>
        <input
          type="text"
          placeholder="Start location"
          value={startName}
          onChange={e => setStartName(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <input
          type="text"
          placeholder="End location"
          value={endName}
          onChange={e => setEndName(e.target.value)}
          style={{ marginRight: "5px" }}
        />
        <button onClick={handleRoute}>Get Route</button>
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <MapContainer center={center} zoom={13} style={{ height: "400px", width: "100%" }}>
  <TileLayer
    attribution="&copy; OpenStreetMap contributors"
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  />

  {route.length > 0 && (
    <>
      {/* Start Marker */}
      <Marker position={route[0]}>
        <Popup>Start</Popup>
      </Marker>
      
      {/* End Marker */}
      <Marker position={route[route.length - 1]}>
        <Popup>End</Popup>
      </Marker>

      {/* Polyline for route */}
      <Polyline positions={route} color="blue" />
    </>
  )}
</MapContainer>

    </div>
  );
}
export default MapView;
