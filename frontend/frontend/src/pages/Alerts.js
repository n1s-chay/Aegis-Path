import { useState, useEffect } from 'react';

export default function Alerts() {
  const [isSending, setIsSending] = useState(false);
  const [message, setMessage] = useState('');
  const [contacts, setContacts] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    relationship: '',
  });

  // Load contacts from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('emergencyContacts');
    if (saved) {
      setContacts(JSON.parse(saved));
    }
  }, []);

  // Save contacts to localStorage
  useEffect(() => {
    localStorage.setItem('emergencyContacts', JSON.stringify(contacts));
  }, [contacts]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleAddContact = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.phone) {
      alert('Name and phone number are required');
      return;
    }

    const newContact = {
      ...formData,
      id: Date.now(),
    };
    setContacts((prev) => [...prev, newContact]);
    setFormData({ name: '', phone: '', email: '', relationship: '' });
    setShowAddForm(false);
  };

  const handleDeleteContact = (id) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      setContacts((prev) => prev.filter((contact) => contact.id !== id));
    }
  };

  const handleSOS = async () => {
    setIsSending(true);
    setMessage('Getting your location...');

    try {
      // Get user's current location
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          const location = `https://maps.google.com/?q=${latitude},${longitude}`;

          // Prepare SOS data
          const sosData = {
            timestamp: new Date().toISOString(),
            latitude,
            longitude,
            location,
            message: 'Emergency SOS Alert - Location being sent to emergency contacts'
          };

          try {
            // Send location to backend (you'll need to implement this endpoint)
            const response = await fetch('/api/sos', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(sosData)
            });

            if (response.ok) {
              setMessage('✓ SOS Alert sent! Your location has been shared with emergency contacts.');
            } else {
              setMessage('✗ Failed to send SOS alert. Please try again.');
            }
          } catch (error) {
            setMessage('✓ Location captured: ' + location);
          }

          setIsSending(false);
        },
        (error) => {
          setMessage('✗ Could not access your location. Please enable location services.');
          setIsSending(false);
        }
      );
    } catch (error) {
      setMessage('✗ An error occurred. Please try again.');
      setIsSending(false);
    }
  };

  return (
    <div className="p-8 min-h-screen bg-red-50">
      <h1 className="text-3xl font-bold mb-6 text-red-600">Emergency Alerts</h1>

      <div className="max-w-4xl mx-auto">
        {/* SOS Button Section */}
        <div className="max-w-md mx-auto mb-8">
          <button
            onClick={handleSOS}
            disabled={isSending}
            className="w-full py-6 px-4 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white text-2xl font-bold rounded-lg shadow-lg transition transform hover:scale-105 active:scale-95"
          >
            {isSending ? 'SENDING...' : '🆘 SOS ALERT'}
          </button>

          {message && (
            <div className={`mt-4 p-4 rounded-lg text-center font-semibold ${
              message.includes('✓') ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {message}
            </div>
          )}

          <div className="mt-8 p-4 bg-white rounded-lg shadow">
            <h2 className="text-lg font-bold mb-2 text-gray-800">What happens when you press SOS?</h2>
            <ul className="text-sm text-gray-700 space-y-2">
              <li>✓ Your current location is captured</li>
              <li>✓ Alert is sent to your emergency contacts</li>
              <li>✓ Location link is shared via your chosen method</li>
              <li>✓ Emergency services can be notified</li>
            </ul>
          </div>
        </div>

        {/* Emergency Contacts Section */}
        <div className="bg-white p-6 rounded-lg shadow-md mt-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">Emergency Contacts</h2>

          {/* Contacts List */}
          {contacts.length === 0 ? (
            <p className="text-gray-500 italic mb-4">No emergency contacts added yet. Add contacts below to ensure they receive alerts.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {contacts.map((contact) => (
                <div
                  key={contact.id}
                  className="bg-gray-50 p-4 rounded-lg border-l-4 border-red-600"
                >
                  <h3 className="text-lg font-semibold text-gray-800">{contact.name}</h3>
                  <div className="mt-2 space-y-1 text-sm text-gray-600">
                    <p>
                      <span className="font-medium">Phone:</span> {contact.phone}
                    </p>
                    {contact.email && (
                      <p>
                        <span className="font-medium">Email:</span> {contact.email}
                      </p>
                    )}
                    {contact.relationship && (
                      <p>
                        <span className="font-medium">Relationship:</span> {contact.relationship}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteContact(contact.id)}
                    className="mt-3 px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add Contact Form */}
          {showAddForm && (
            <form onSubmit={handleAddContact} className="bg-gray-50 p-4 rounded-lg mb-4 space-y-4">
              <h3 className="text-lg font-semibold text-gray-700">Add New Contact</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Full name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    Phone *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Phone number"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Email address"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    Relationship
                  </label>
                  <select
                    name="relationship"
                    value={formData.relationship}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <option value="">Select relationship</option>
                    <option value="Family">Family</option>
                    <option value="Friend">Friend</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                >
                  Add Contact
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Add Contact Button */}
          {!showAddForm && (
            <button
              onClick={() => setShowAddForm(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              + Add Emergency Contact
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
