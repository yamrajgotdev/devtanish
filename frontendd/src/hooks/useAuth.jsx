import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('auth_token');
      if (!storedUser || !token) {
        setLoading(false);
        return;
      }
      try {
        await authService.getProfile();
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };
    restoreSession();
  }, []);

  const login = async (phone_number) => {
    const response = await authService.login(phone_number);
    return response.data;
  };

  const verifyOTP = async (phone_number, otp) => {
    const response = await authService.verifyOTP(phone_number, otp);
    const { user, is_new_user, token } = response.data;
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify({ ...user, phone_number }));
    setUser({ ...user, phone_number });
    return { user, is_new_user };
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const updateUser = (userData) => {
    const updated = { ...user, ...userData };
    setUser(updated);
    localStorage.setItem('user', JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, verifyOTP, logout, updateUser, isDriver: user?.is_driver }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
