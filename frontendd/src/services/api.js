import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (phone_number) => api.post('/auth/login/', { phone_number }),
  verifyOTP: (phone_number, otp) => api.post('/auth/verify/', { phone_number, otp }),
  getProfile: () => api.get('/user/profile'),
};

export const driverService = {
  register: (data) => api.post('/drivers/register/', data),
  toggleOnline: (phone_number) => api.post('/drivers/toggle-online/', { phone_number }),
  updateLocation: (phone_number, lat, lng) => 
    api.post('/drivers/update-location/', { phone_number, lat, lng }),
  getNearby: (lat, lng, radius, vehicle_type) => 
    api.get(`/drivers/nearby/?lat=${lat}&lng=${lng}&radius=${radius || 10}&vehicle_type=${vehicle_type || ''}`),
  uploadDocuments: (phone_number, files) => {
    const formData = new FormData();
    formData.append('phone_number', phone_number);
    Object.entries(files).forEach(([key, file]) => {
      if (file) formData.append(key, file);
    });
    return api.post('/drivers/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const rideService = {
  request: (data) => api.post('/rides/request/', data),
  getStatus: (ride_id) => api.get(`/rides/status/${ride_id}/`),
  accept: (ride_id, phone_number) => 
    api.post('/rides/accept/', { ride_id, phone_number }),
  updateStatus: (ride_id, phone_number, status) => 
    api.post('/rides/update-status/', { ride_id, phone_number, status }),
  cancel: (ride_id, phone_number) => 
    api.post('/rides/cancel/', { ride_id, phone_number }),
  getPassengerRides: (phone_number) => 
    api.get(`/rides/passenger/?phone_number=${phone_number}`),
  getDriverRides: (phone_number) => 
    api.get(`/rides/driver/?phone_number=${phone_number}`),
  getUserRides: () => api.get('/user/rides'),
};

export const mapsService = {
  geocode: (address) => api.get(`/maps/geocode/?address=${encodeURIComponent(address)}`),
  reverseGeocode: (lat, lng) => api.get(`/maps/reverse-geocode/?lat=${lat}&lng=${lng}`),
  autocomplete: (input) => api.get(`/maps/autocomplete/?input=${encodeURIComponent(input)}`),
  route: (origin_lat, origin_lng, dest_lat, dest_lng) => 
    api.get(`/maps/route/?origin_lat=${origin_lat}&origin_lng=${origin_lng}&dest_lat=${dest_lat}&dest_lng=${dest_lng}`),
};

export const healthCheck = () => api.get('/');

export default api;
