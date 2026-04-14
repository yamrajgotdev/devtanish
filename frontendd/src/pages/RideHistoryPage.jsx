import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rideService } from '../services/api';

function getGroupLabel(dateValue) {
  const now = new Date();
  const date = new Date(dateValue);
  const dayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const weekStart = new Date(dayStart);
  weekStart.setDate(dayStart.getDate() - 7);
  if (date >= dayStart) return 'Today';
  if (date >= weekStart) return 'This Week';
  return 'Earlier';
}

export default function RideHistoryPage() {
  const navigate = useNavigate();
  const [rides, setRides] = useState([]);
  const [totalRides, setTotalRides] = useState(0);
  const [selectedRide, setSelectedRide] = useState(null);

  useEffect(() => {
    const load = async () => {
      const response = await rideService.getUserRides();
      setRides(response.data?.rides || []);
      setTotalRides(response.data?.total_rides || 0);
    };
    load();
  }, []);

  const groupedRides = useMemo(() => {
    return rides.reduce((acc, ride) => {
      const key = getGroupLabel(ride.date);
      if (!acc[key]) acc[key] = [];
      acc[key].push(ride);
      return acc;
    }, {});
  }, [rides]);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Ride History</h1>
          <button onClick={() => navigate('/')} className="px-4 py-2 bg-white rounded-lg border">
            Back
          </button>
        </div>
        <p className="text-sm text-gray-600 mb-4">Total rides: {totalRides}</p>

        {Object.entries(groupedRides).map(([group, groupItems]) => (
          <div key={group} className="mb-6">
            <h2 className="text-sm font-semibold text-gray-500 mb-2 uppercase">{group}</h2>
            <div className="space-y-3">
              {groupItems.map((ride) => (
                <button
                  type="button"
                  key={ride.ride_id}
                  onClick={() => setSelectedRide(ride)}
                  className="w-full text-left bg-white rounded-xl p-4 border hover:shadow-sm"
                >
                  <div className="font-semibold text-gray-800">{ride.pickup} {'->'} {ride.destination}</div>
                  <div className="text-sm text-gray-600 mt-1">
                    Driver: {ride.driver_name} | Fare: INR {Math.round(ride.fare || 0)} | Status: {ride.ride_status}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{new Date(ride.date).toLocaleString()}</div>
                </button>
              ))}
            </div>
          </div>
        ))}

        {selectedRide && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl p-5 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-3">Ride Details</h3>
              <p className="text-sm mb-1"><strong>Pickup:</strong> {selectedRide.pickup}</p>
              <p className="text-sm mb-1"><strong>Destination:</strong> {selectedRide.destination}</p>
              <p className="text-sm mb-1"><strong>Driver:</strong> {selectedRide.driver_name}</p>
              <p className="text-sm mb-1"><strong>Fare:</strong> INR {Math.round(selectedRide.fare || 0)}</p>
              <p className="text-sm mb-1"><strong>Status:</strong> {selectedRide.ride_status}</p>
              <p className="text-sm mb-4"><strong>Date:</strong> {new Date(selectedRide.date).toLocaleString()}</p>
              <button onClick={() => setSelectedRide(null)} className="w-full py-2 bg-primary-500 text-white rounded-lg">
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
