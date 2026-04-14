import { useEffect, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';
import { mapsService } from '../services/api';

export default function DestinationSearch({ onSelect }) {
  const [query, setQuery] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length < 2) {
      setPredictions([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      try {
        setLoading(true);
        const response = await mapsService.autocomplete(query.trim());
        const list = response.data?.predictions || [];
        setPredictions(list);
        setOpen(true);
      } catch (error) {
        console.error('Destination autocomplete failed:', error);
        setPredictions([]);
      } finally {
        setLoading(false);
      }
    }, 350);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSelect = (item) => {
    setQuery(item.place_name || item.description);
    setPredictions([]);
    setOpen(false);
    onSelect?.(item);
  };

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onFocus={() => predictions.length > 0 && setOpen(true)}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search destination"
          className="w-full pl-10 pr-10 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:outline-none transition-colors"
        />
        {!!query && (
          <button
            type="button"
            onClick={() => {
              setQuery('');
              setPredictions([]);
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-full"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>

      {loading && (
        <div className="absolute z-40 w-full mt-2 bg-white rounded-xl shadow-xl border border-gray-100 p-4 text-sm text-gray-500">
          Searching places...
        </div>
      )}

      {open && predictions.length > 0 && (
        <div className="absolute z-40 w-full mt-2 bg-white rounded-xl shadow-xl border border-gray-100 max-h-72 overflow-y-auto">
          {predictions.map((item, index) => (
            <button
              key={`${item.place_id || item.description}-${index}`}
              type="button"
              onClick={() => handleSelect(item)}
              className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
            >
              <div className="font-medium text-gray-800 line-clamp-1">
                {item.place_name || item.description}
              </div>
              <div className="text-xs text-gray-500 line-clamp-1">
                {item.secondary_text || item.description}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
