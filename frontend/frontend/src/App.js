import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import MapView from "./pages/MapView";
import Alerts from "./pages/Alerts";

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: 20 }}>
        {/* Navigation bar */}
        <nav style={{ marginBottom: 20 }}>
          <Link to="/" style={{ marginRight: 15 }}>Home</Link>
          <Link to="/map" style={{ marginRight: 15 }}>Map</Link>
          <Link to="/alerts">Alerts</Link>
        </nav>

        {/* Page content */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/map" element={<MapView />} />
          <Route path="/alerts" element={<Alerts />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

