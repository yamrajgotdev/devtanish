export default function DriverCard({ driver, onAccept, showAccept = false, isAccepting = false }) {
  if (!driver) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg p-4">
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 bg-primary-100 rounded-full flex items-center justify-center text-2xl">
          👤
        </div>
        <div className="flex-1">
          <div className="font-bold text-gray-800">{driver.name || 'Driver'}</div>
          <div className="text-sm text-gray-500">{driver.vehicle_type?.toUpperCase()} • {driver.vehicle_number || 'N/A'}</div>
          <div className="flex items-center gap-1 mt-1">
            <span className="text-yellow-500">⭐</span>
            <span className="text-sm font-medium">{driver.rating || 4.5}</span>
            {driver.distance_km && (
              <span className="text-sm text-gray-400 ml-2">{driver.distance_km} km away</span>
            )}
          </div>
        </div>
        {showAccept && (
          <button
            onClick={() => onAccept?.(driver.id)}
            disabled={isAccepting}
            className="px-4 py-2 bg-green-500 text-white font-semibold rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
          >
            {isAccepting ? 'Accepting...' : 'Accept'}
          </button>
        )}
      </div>
    </div>
  );
}
