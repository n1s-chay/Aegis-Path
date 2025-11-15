import { useState, useEffect } from 'react';

export default function MapView() {
  const [destination, setDestination] = useState('');
  const [currentLocation, setCurrentLocation] = useState(null);
  const [locationError, setLocationError] = useState('');
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [route, setRoute] = useState(null);
  const [manualLocation, setManualLocation] = useState('');
  const [showManualEntry, setShowManualEntry] = useState(false);

  // Auto-detect current location on page load
  useEffect(() => {
    getAutoLocation();
  }, []);

  const getAutoLocation = () => {
    setIsLoadingLocation(true);
    setLocationError('');
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setCurrentLocation({ latitude, longitude });
          setIsLoadingLocation(false);
        },
        (error) => {
          setLocationError('Could not access your location. Please enable location services or enter manually.');
          setIsLoadingLocation(false);
        }
      );
    } else {
      setLocationError('Geolocation is not supported by your browser.');
      setIsLoadingLocation(false);
    }
  };

  const handleManualLocation = () => {
    if (!manualLocation.trim()) {
      alert('Please enter a landmark or address');
      return;
    }
    // For demo purposes, we'll use mock coordinates
    const mockLat = (28.5 + Math.random() * 0.5).toFixed(6);
    const mockLng = (77.1 + Math.random() * 0.5).toFixed(6);
    setCurrentLocation({ 
      latitude: parseFloat(mockLat), 
      longitude: parseFloat(mockLng),
      landmark: manualLocation
    });
    setShowManualEntry(false);
    setManualLocation('');
    setLocationError('');
  };

  const handleSearchRoute = () => {
    if (!destination) {
      alert('Please enter a destination');
      return;
    }
    if (!currentLocation) {
      alert('Please set your current location first');
      return;
    }

    // Create a mock route
    setRoute({
      from: `${currentLocation.latitude.toFixed(4)}, ${currentLocation.longitude.toFixed(4)}`,
      to: destination,
      risk: Math.random() > 0.5 ? 'Low' : 'High',
      distance: Math.floor(Math.random() * 20) + 1,
      estimatedTime: Math.floor(Math.random() * 45) + 5
    });
  };

  return (
    <div className="p-8 min-h-screen bg-blue-50">
      <h1 className="text-3xl font-bold mb-6 text-blue-600">Route Planner</h1>

      {/* Current Location Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Your Current Location</h2>
        
        {isLoadingLocation && <p className="text-blue-600">📍 Detecting your location...</p>}
        
        {currentLocation && (
          <div className="bg-green-50 p-4 rounded-lg mb-4 border-l-4 border-green-600">
            <p className="text-green-800 font-semibold">✓ Location Found</p>
            <p className="text-gray-700 text-sm mt-2">
              Latitude: {currentLocation.latitude.toFixed(6)}
            </p>
            <p className="text-gray-700 text-sm">
              Longitude: {currentLocation.longitude.toFixed(6)}
            </p>
            <p className="text-gray-700 text-sm">
              <a 
                href={`https://maps.google.com/?q=${currentLocation.latitude},${currentLocation.longitude}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                View on Google Maps
              </a>
            </p>
          </div>
        )}

        {locationError && (
          <div className="bg-yellow-50 p-4 rounded-lg mb-4 border-l-4 border-yellow-600">
            <p className="text-yellow-800 text-sm">{locationError}</p>
          </div>
        )}

        <div className="flex gap-2 mb-4">
          <button
            onClick={getAutoLocation}
            disabled={isLoadingLocation}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            🔄 Auto-Detect Location
          </button>
          <button
            onClick={() => setShowManualEntry(!showManualEntry)}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
          >
            ✏️ Enter Manually
          </button>
        </div>

        {/* Manual Location Entry */}
        {showManualEntry && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Landmark or Address</label>
              <input
                type="text"
                value={manualLocation}
                onChange={(e) => setManualLocation(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Central Park, Times Square, Home"
              />
            </div>
            <button
              onClick={handleManualLocation}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Set Location
            </button>
          </div>
        )}
      </div>

      {/* Destination Section */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Destination</h2>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">Where do you want to go?</label>
            <input
              type="text"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter destination address, landmark, or place name"
            />
          </div>
          <button
            onClick={handleSearchRoute}
            className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
          >
            🗺️ Search Route
          </button>
        </div>
      </div>

      {/* Route Results */}
      {route && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Route Details</h2>
          <div className="space-y-3">
            <div className="border-l-4 border-blue-600 pl-4 py-2">
              <p className="text-gray-600 text-sm">From</p>
              <p className="font-semibold text-gray-800">{route.from}</p>
            </div>
            <div className="border-l-4 border-blue-600 pl-4 py-2">
              <p className="text-gray-600 text-sm">To</p>
              <p className="font-semibold text-gray-800">{route.to}</p>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-600 text-sm">Safety Risk</p>
                <p className={`font-bold ${route.risk === 'High' ? 'text-red-600' : 'text-green-600'}`}>
                  {route.risk}
                </p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-600 text-sm">Distance</p>
                <p className="font-bold text-gray-800">{route.distance} km</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-gray-600 text-sm">Est. Time</p>
                <p className="font-bold text-gray-800">{route.estimatedTime} min</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
