import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';
import { OlaMaps } from 'olamaps-web-sdk';
import { mapsService } from '../services/api';

const apiKey = import.meta.env.VITE_OLA_MAPS_API_KEY || '';

const MapContainer = forwardRef(function MapContainer({ center, pickup }, ref) {
  const mapNodeRef = useRef(null);
  const mapRef = useRef(null);
  const olaRef = useRef(null);
  const pickupMarkerRef = useRef(null);
  const destinationMarkerRef = useRef(null);
  const [ready, setReady] = useState(false);

  const clearRoute = () => {
    if (!mapRef.current) return;
    if (mapRef.current.getLayer('route-line')) mapRef.current.removeLayer('route-line');
    if (mapRef.current.getSource('route')) mapRef.current.removeSource('route');
  };

  const addRouteLine = (coordinates) => {
    if (!mapRef.current || !coordinates?.length) return;
    clearRoute();
    
    // Ensure coordinates are in the correct format [lng, lat]
    const formattedCoordinates = coordinates.map(coord => {
      if (Array.isArray(coord) && coord.length >= 2) {
        return [coord[0], coord[1]]; // [lng, lat]
      }
      return coord;
    });
    
    mapRef.current.addSource('route', {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: { type: 'LineString', coordinates: formattedCoordinates },
      },
    });
    mapRef.current.addLayer({
      id: 'route-line',
      type: 'line',
      source: 'route',
      layout: { 'line-join': 'round', 'line-cap': 'round' },
      paint: { 'line-color': '#2563eb', 'line-width': 6, 'line-opacity': 0.9 },
    });
  };

  useEffect(() => {
    if (!mapNodeRef.current || mapRef.current || !apiKey) return;
    
    try {
      const ola = new OlaMaps({ apiKey });
      const map = ola.init({
        style: `https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json?api_key=${apiKey}`,
        container: mapNodeRef.current,
        center: [center?.lng || 72.8777, center?.lat || 19.076],
        zoom: 14,
      });
      olaRef.current = ola;
      mapRef.current = map;
      map.on('load', () => setReady(true));

      return () => {
        if (mapRef.current) {
          mapRef.current.remove();
        }
        mapRef.current = null;
        olaRef.current = null;
        pickupMarkerRef.current = null;
        destinationMarkerRef.current = null;
      };
    } catch (error) {
      console.error('Map initialization error:', error);
    }
  }, [center, apiKey]);

  useEffect(() => {
    if (!ready || !pickup || !olaRef.current || !mapRef.current) return;
    
    if (!pickupMarkerRef.current) {
      pickupMarkerRef.current = olaRef.current
        .addMarker({ markerId: 'pickup', color: '#16a34a' })
        .setLngLat([pickup.lng, pickup.lat])
        .addTo(mapRef.current);
    } else {
      pickupMarkerRef.current.setLngLat([pickup.lng, pickup.lat]);
    }
    mapRef.current.easeTo({ center: [pickup.lng, pickup.lat], zoom: 14 });
  }, [pickup, ready]);

  useImperativeHandle(ref, () => ({
    setDestinationMarker: ({ lat, lng }) => {
      if (!ready || !olaRef.current || !mapRef.current) return;
      
      if (!destinationMarkerRef.current) {
        destinationMarkerRef.current = olaRef.current
          .addMarker({ markerId: 'destination', color: '#dc2626' })
          .setLngLat([lng, lat])
          .addTo(mapRef.current);
      } else {
        destinationMarkerRef.current.setLngLat([lng, lat]);
      }
      mapRef.current.flyTo({ center: [lng, lat], zoom: 14 });
    },
    drawRoute: async ({ origin, destination }) => {
      if (!ready || !origin || !destination) return;
      
      try {
        const response = await mapsService.route(origin.lat, origin.lng, destination.lat, destination.lng);
        const routeData = response.data;
        const routeGeometry = routeData?.route?.geometry;
        
        if (Array.isArray(routeGeometry) && routeGeometry.length > 0) {
          addRouteLine(routeGeometry);
        }
      } catch (error) {
        console.error('Route drawing failed:', error);
      }
    },
  }));

  return <div ref={mapNodeRef} className="absolute inset-0 h-full w-full" />;
});

export default MapContainer;
