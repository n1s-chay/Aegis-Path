export function fetchIncidents() {
  return fetch("http://localhost:5000/api/incidents")
    .then(res => res.json());
}
