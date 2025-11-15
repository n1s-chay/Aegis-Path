import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="p-8 text-center bg-yellow-50 min-h-screen">
      <h1 className="text-4xl font-bold mb-4 text-blue-600">Welcome to AegisPath</h1>
      <button 
        onClick={() => navigate('/map')}
        className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Get Started
      </button>
    </div>
  );
}
