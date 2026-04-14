import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const load = async () => {
      const response = await authService.getProfile();
      setProfile(response.data || null);
    };
    load();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-xl mx-auto bg-white border rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Profile</h1>
          <button onClick={() => navigate('/')} className="px-4 py-2 bg-gray-100 rounded-lg">
            Back
          </button>
        </div>

        {!profile ? (
          <p className="text-gray-600">Loading profile...</p>
        ) : (
          <div className="space-y-3">
            <div><strong>Phone Number:</strong> {profile.phone_number}</div>
            <div><strong>Total Rides:</strong> {profile.total_rides}</div>
            <div><strong>Member Since:</strong> {new Date(profile.member_since).toLocaleString()}</div>
            <div><strong>Last Login:</strong> {profile.last_login ? new Date(profile.last_login).toLocaleString() : '-'}</div>
          </div>
        )}
      </div>
    </div>
  );
}
