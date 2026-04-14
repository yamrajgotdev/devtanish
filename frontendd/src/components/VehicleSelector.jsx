const vehicleTypes = [
  {
    id: 'bike',
    name: 'Bike',
    description: 'Fast & affordable',
    icon: '🏍️',
    multiplier: 0.6,
    capacity: '1 passenger',
  },
  {
    id: 'auto',
    name: 'Auto',
    description: 'Affordable rides',
    icon: '🛺',
    multiplier: 0.8,
    capacity: '3 passengers',
  },
  {
    id: 'mini',
    name: 'Mini',
    description: 'Compact cars',
    icon: '🚗',
    multiplier: 1.0,
    capacity: '4 passengers',
  },
  {
    id: 'sedan',
    name: 'Sedan',
    description: 'Premium rides',
    icon: '🚙',
    multiplier: 1.4,
    capacity: '4 passengers',
  },
  {
    id: 'suv',
    name: 'SUV',
    description: 'Spacious rides',
    icon: '🚘',
    multiplier: 1.8,
    capacity: '6 passengers',
  },
];

export default function VehicleSelector({ selected, onSelect, fare, distance }) {
  const baseFare = 20;
  const perKm = 10;

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-800">Select Vehicle</h3>
      {vehicleTypes.map((vehicle) => {
        const estimatedFare = Math.round((baseFare + distance * perKm) * vehicle.multiplier);
        return (
          <button
            key={vehicle.id}
            onClick={() => onSelect(vehicle.id)}
            className={`w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
              selected === vehicle.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="text-3xl">{vehicle.icon}</span>
              <div className="text-left">
                <div className="font-semibold text-gray-800">{vehicle.name}</div>
                <div className="text-sm text-gray-500">{vehicle.description}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-gray-800">₹{estimatedFare}</div>
              <div className="text-xs text-gray-500">{vehicle.capacity}</div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

export { vehicleTypes };
