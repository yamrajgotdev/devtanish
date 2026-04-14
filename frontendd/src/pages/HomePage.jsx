import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLocation } from '../hooks/useLocation';
import MapContainer from '../components/MapContainer';
import DestinationSearch from '../components/DestinationSearch';
import { rideService } from '../services/api';
import { Navigation, LogOut, User, History } from 'lucide-react';

export default function HomePage() {
  const { user, logout, updateUser } = useAuth();
  const { location, error: locationError, getLocation } = useLocation();
  const navigate = useNavigate();
  const mapRef = useRef(null);

  const [pickup, setPickup] = useState(null);
  const [destination, setDestination] = useState(null);
  const [destinationLabel, setDestinationLabel] = useState('');
  const [selectedVehicle, setSelectedVehicle] = useState('mini');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (location) {
      setPickup(location);
    }
  }, [location]);

  const handleBookRide = async () => {
    if (!pickup || !destination) {
      setError('Please select destination');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await rideService.request({
        pickup_lat: pickup.lat,
        pickup_lng: pickup.lng,
        drop_lat: destination.lat,
        drop_lng: destination.lng,
        pickup_address: 'Current location',
        drop_address: destinationLabel,
        vehicle_type: selectedVehicle,
      });

      if (response.data.success) {
        updateUser({ total_rides: (user.total_rides || 0) + 1 });
        navigate('/history');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to book ride');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleDestinationSelect = async (selected) => {
    const next = { lat: selected.lat, lng: selected.lng };
    setDestination(next);
    setDestinationLabel(selected.place_name || selected.description);
    mapRef.current?.setDestinationMarker(next);
    if (pickup) {
      await mapRef.current?.drawRoute({
        origin: pickup,
        destination: next,
      });
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden relative">
      <MapContainer ref={mapRef} center={location || { lat: 19.076, lng: 72.877 }} pickup={pickup} />

      <div className="absolute top-4 left-4 right-4 z-20">
        <div className="bg-white rounded-2xl shadow-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-gray-600" />
              <span className="font-medium text-gray-800">{user?.phone_number}</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => navigate('/history')} className="p-2 rounded-full hover:bg-gray-100">
                <History className="w-5 h-5 text-gray-600" />
              </button>
              <button onClick={() => navigate('/profile')} className="p-2 rounded-full hover:bg-gray-100">
                <User className="w-5 h-5 text-gray-600" />
              </button>
              <button onClick={handleLogout} className="p-2 rounded-full hover:bg-gray-100">
                <LogOut className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
          <DestinationSearch onSelect={handleDestinationSelect} />
          <div className="grid grid-cols-4 gap-2 mt-3">
            {['mini', 'sedan', 'suv', 'bike'].map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setSelectedVehicle(type)}
                className={`px-3 py-2 rounded-lg text-sm font-medium ${
                  selectedVehicle === type ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
          {error && <div className="mt-3 text-sm text-red-600">{error}</div>}
          <button
            onClick={handleBookRide}
            disabled={loading || !destination}
            className="mt-3 w-full py-3 bg-primary-500 text-white rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? 'Booking...' : 'Book Ride'}
          </button>
        </div>
      </div>

      <button
        onClick={getLocation}
        className="absolute right-4 bottom-6 z-20 bg-white p-3 rounded-full shadow-lg hover:bg-gray-100"
      >
        <Navigation className="w-6 h-6 text-primary-500" />
      </button>

      {locationError && (
        <div className="absolute bottom-20 left-4 right-4 z-20 bg-red-500 text-white p-4 rounded-xl">
          <p className="font-medium">Location Error</p>
          <p className="text-sm">{locationError}</p>
          <button onClick={getLocation} className="mt-2 text-sm underline">
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
