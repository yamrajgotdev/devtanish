export default function RideCard({ ride, onAction, actionLabel, actionType }) {
  if (!ride) return null;

  const statusColors = {
    requested: 'bg-yellow-100 text-yellow-700',
    searching_driver: 'bg-yellow-100 text-yellow-700',
    driver_assigned: 'bg-blue-100 text-blue-700',
    driver_arriving: 'bg-blue-100 text-blue-700',
    ride_started: 'bg-green-100 text-green-700',
    ride_completed: 'bg-gray-100 text-gray-700',
    cancelled: 'bg-red-100 text-red-700',
  };

  const statusLabels = {
    requested: 'Requested',
    searching_driver: 'Searching Driver',
    driver_assigned: 'Driver Assigned',
    driver_arriving: 'Driver Arriving',
    ride_started: 'In Progress',
    ride_completed: 'Completed',
    cancelled: 'Cancelled',
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-4">
      <div className="flex justify-between items-start mb-3">
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[ride.status] || 'bg-gray-100'}`}>
          {statusLabels[ride.status] || ride.status}
        </span>
        <span className="text-lg font-bold text-gray-800">₹{ride.estimated_fare || ride.price}</span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-start gap-3">
          <div className="w-3 h-3 rounded-full bg-green-500 mt-1.5" />
          <div className="flex-1">
            <div className="text-sm text-gray-500">Pickup</div>
            <div className="text-gray-800">{ride.pickup_address || 'Not specified'}</div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500 mt-1.5" />
          <div className="flex-1">
            <div className="text-sm text-gray-500">Drop</div>
            <div className="text-gray-800">{ride.drop_address || 'Not specified'}</div>
          </div>
        </div>
      </div>

      {ride.distance_km && (
        <div className="text-sm text-gray-500 mb-3">
          Distance: {ride.distance_km} km
        </div>
      )}

      {ride.driver_details && (
        <div className="border-t border-gray-100 pt-3 mb-3">
          <div className="text-sm font-medium text-gray-700 mb-2">Driver Info</div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">👤</div>
            <div>
              <div className="font-medium">{ride.driver_details.name}</div>
              <div className="text-sm text-gray-500">{ride.driver_details.vehicle_number}</div>
            </div>
          </div>
        </div>
      )}

      {ride.otp && ride.status !== 'ride_completed' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
          <div className="text-sm text-yellow-800">
            <span className="font-medium">OTP:</span> {ride.otp}
          </div>
        </div>
      )}

      {onAction && (
        <button
          onClick={() => onAction()}
          className={`w-full py-3 rounded-xl font-semibold transition-colors ${
            actionType === 'cancel'
              ? 'bg-red-500 text-white hover:bg-red-600'
              : actionType === 'complete'
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'bg-primary-500 text-white hover:bg-primary-600'
          }`}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
