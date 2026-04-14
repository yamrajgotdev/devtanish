import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useLocation } from '../hooks/useLocation';
import MapContainer from '../components/MapContainer';
import BottomSheetPanel from '../components/BottomSheetPanel';
import RideCard from '../components/RideCard';
import { rideService, driverService } from '../services/api';
import { LogOut, User, Phone, Car, MapPin, Navigation, Clock, CheckCircle } from 'lucide-react';

export default function DriverDashboard() {
  const { user, logout, updateUser } = useAuth();
  const { location, getLocation } = useLocation();
  const navigate = useNavigate();

  const [isOnline, setIsOnline] = useState(false);
  const [isApproved, setIsApproved] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentRide, setCurrentRide] = useState(null);
  const [availableRides, setAvailableRides] = useState([]);
  const [panelState, setPanelState] = useState('dashboard');
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    if (user && user.is_driver) {
      fetchDriverProfile();
    } else {
      registerAsDriver();
    }
  }, [user]);

  useEffect(() => {
    if (!isOnline || !location) return;

    const updateLocation = async () => {
      try {
        await driverService.updateLocation(user.phone_number, location.lat, location.lng);
      } catch (err) {
        console.error('Location update failed:', err);
      }
    };

    updateLocation();
    const interval = setInterval(updateLocation, 5000);
    return () => clearInterval(interval);
  }, [isOnline, location, user]);

  useEffect(() => {
    if (!isOnline) return;

    const fetchAvailableRides = async () => {
      try {
        const response = await rideService.getPassengerRides(user.phone_number);
        if (response.data.success) {
          const pending = response.data.rides?.filter(
            r => r.status === 'requested' || r.status === 'searching_driver'
          ) || [];
          setAvailableRides(pending);
        }
      } catch (err) {
        console.error('Fetch rides error:', err);
      }
    };

    fetchAvailableRides();
    const interval = setInterval(fetchAvailableRides, 5000);
    return () => clearInterval(interval);
  }, [isOnline, user]);

  useEffect(() => {
    if (!currentRide) return;

    const pollStatus = async () => {
      try {
        const response = await rideService.getStatus(currentRide.id);
        if (response.data.success) {
          setCurrentRide(response.data.ride);
          if (response.data.ride.status === 'ride_completed') {
            setCurrentRide(null);
            setPanelState('dashboard');
          }
        }
      } catch (err) {
        console.error('Poll status error:', err);
      }
    };

    const interval = setInterval(pollStatus, 3000);
    return () => clearInterval(interval);
  }, [currentRide]);

  const fetchDriverProfile = async () => {
    try {
      const response = await driverService.toggleOnline(user.phone_number);
      setIsOnline(response.data.is_online);
    } catch (err) {
      console.error('Profile fetch error:', err);
    }
  };

  const registerAsDriver = async () => {
    setLoading(true);
    try {
      await driverService.register({
        phone_number: user.phone_number,
        name: user.name || 'Driver',
        vehicle_type: 'mini',
      });
      updateUser({ ...user, is_driver: true });
    } catch (err) {
      console.error('Driver registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleOnline = async () => {
    setLoading(true);
    try {
      const response = await driverService.toggleOnline(user.phone_number);
      setIsOnline(response.data.is_online);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to toggle status');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRide = async (rideId) => {
    setAccepting(true);
    try {
      const response = await rideService.accept(rideId, user.phone_number);
      if (response.data.success) {
        setCurrentRide(response.data.ride);
        setPanelState('active');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to accept ride');
    } finally {
      setAccepting(false);
    }
  };

  const updateRideStatus = async (newStatus) => {
    if (!currentRide) return;
    try {
      const response = await rideService.updateStatus(currentRide.id, user.phone_number, newStatus);
      if (response.data.success) {
        setCurrentRide({ ...currentRide, status: newStatus });
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update status');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isOnRide = currentRide && !['cancelled', 'ride_completed'].includes(currentRide.status);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-gray-50">
      <div className="flex-1 relative">
        <MapContainer center={location || { lat: 19.076, lng: 72.877 }} pickup={location} />

        <div className="absolute top-4 left-4 right-4 z-10">
          <div className="bg-white rounded-xl shadow-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                  <Car className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <div className="font-bold text-gray-800">{user?.name || 'Driver'}</div>
                  <div className="text-sm text-gray-500">{user?.phone_number}</div>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <LogOut className="w-5 h-5 text-gray-600" />
              </button>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={getLocation}
                className="p-2 bg-gray-100 rounded-full hover:bg-gray-200"
              >
                <Navigation className="w-5 h-5 text-gray-600" />
              </button>
              <button
                onClick={toggleOnline}
                disabled={loading || !isApproved}
                className={`flex-1 py-3 rounded-xl font-bold transition-colors ${
                  isOnline
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-green-500 text-white hover:bg-green-600'
                } disabled:opacity-50`}
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto" />
                ) : isOnline ? (
                  'GO OFFLINE'
                ) : (
                  'GO ONLINE'
                )}
              </button>
            </div>

            {!isApproved && (
              <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-xl text-sm text-yellow-700">
                Your account is pending approval. Please contact support.
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="absolute top-32 left-4 right-4 z-20 bg-red-500 text-white p-4 rounded-xl">
            {error}
            <button onClick={() => setError('')} className="ml-2 underline">Dismiss</button>
          </div>
        )}
      </div>

      {isOnRide ? (
        <BottomSheetPanel isOpen={true} onClose={() => {}} title="Current Ride">
          <div className="space-y-4">
            <RideCard
              ride={currentRide}
              actionType="complete"
              actionLabel={
                currentRide.status === 'driver_assigned' ? 'Start Ride' :
                currentRide.status === 'driver_arriving' ? 'Start Ride' :
                currentRide.status === 'ride_started' ? 'Complete Ride' : null
              }
              onAction={() => {
                if (currentRide.status === 'driver_assigned') {
                  updateRideStatus('driver_arriving');
                } else if (currentRide.status === 'driver_arriving') {
                  updateRideStatus('ride_started');
                } else if (currentRide.status === 'ride_started') {
                  updateRideStatus('ride_completed');
                }
              }}
            />
          </div>
        </BottomSheetPanel>
      ) : (
        <BottomSheetPanel
          isOpen={isOnline && panelState === 'dashboard'}
          onClose={() => setPanelState('dashboard')}
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-800">Available Rides</h2>
              <span className="text-sm text-gray-500">{availableRides.length} requests</span>
            </div>

            {availableRides.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-3">🚗</div>
                <p className="text-gray-500">No ride requests yet</p>
                <p className="text-sm text-gray-400">Waiting for customers...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {availableRides.map((ride) => (
                  <div key={ride.id} className="bg-white rounded-xl border border-gray-200 p-4">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <MapPin className="w-5 h-5 text-primary-500" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-gray-500">Pickup</div>
                        <div className="text-gray-800">{ride.pickup_address || 'Not specified'}</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                        <Navigation className="w-5 h-5 text-red-500" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-gray-500">Drop</div>
                        <div className="text-gray-800">{ride.drop_address || 'Not specified'}</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {ride.distance_km} km
                      </span>
                      <span className="font-bold text-lg text-gray-800">₹{ride.estimated_fare}</span>
                    </div>
                    <button
                      onClick={() => handleAcceptRide(ride.id)}
                      disabled={accepting}
                      className="w-full py-3 bg-green-500 text-white font-bold rounded-xl hover:bg-green-600 disabled:opacity-50"
                    >
                      {accepting ? 'Accepting...' : 'Accept Ride'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </BottomSheetPanel>
      )}
    </div>
  );
}
