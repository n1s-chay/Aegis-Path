import React, { useEffect, useState } from "react";

function Alerts() {
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/incidents")
      .then(res => res.json())
      .then(data => setIncidents(data));
  }, []);

  return (
    <div>
      <h2>Incidents</h2>
      <ul>
        {incidents.map((item, idx) => (
          <li key={idx}>{item.description} ({item.lat}, {item.lng})</li>
        ))}
      </ul>
    </div>
  );
}

export default Alerts;
