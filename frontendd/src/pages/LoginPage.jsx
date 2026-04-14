import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import OTPInput from '../components/OTPInput';
import { Car, Phone } from 'lucide-react';

export default function LoginPage() {
  const [step, setStep] = useState('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, verifyOTP } = useAuth();
  const navigate = useNavigate();

  const handlePhoneSubmit = async (e) => {
    e.preventDefault();
    if (phone.length < 10) {
      setError('Please enter a valid phone number');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await login(phone);
      setStep('otp');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPComplete = async (enteredOtp) => {
    setLoading(true);
    setError('');
    
    try {
      await verifyOTP(phone, enteredOtp);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid OTP');
      setOtp('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700 flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Car className="w-10 h-10 text-primary-500" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">RideGo</h1>
            <p className="text-primary-100">Your ride, your way</p>
          </div>

          <div className="bg-white rounded-3xl shadow-2xl p-8">
            {step === 'phone' ? (
              <>
                <h2 className="text-xl font-bold text-gray-800 mb-6">Login with Phone</h2>
                
                <form onSubmit={handlePhoneSubmit}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <div className="flex">
                      <span className="inline-flex items-center px-4 bg-gray-100 border border-r-0 border-gray-300 rounded-l-xl text-gray-500">
                        +91
                      </span>
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                        placeholder="Enter phone number"
                        className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-r-xl focus:border-primary-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {error && (
                    <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm">
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-4 bg-primary-500 text-white font-bold rounded-xl hover:bg-primary-600 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <Phone className="w-5 h-5" />
                        Get OTP
                      </>
                    )}
                  </button>
                </form>
              </>
            ) : (
              <>
                <h2 className="text-xl font-bold text-gray-800 mb-2">Enter OTP</h2>
                <p className="text-gray-500 text-sm mb-6">
                  We sent a code to +91 {phone}
                </p>

                <div className="mb-6">
                  <OTPInput onComplete={handleOTPComplete} />
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm">
                    {error}
                  </div>
                )}

                <p className="text-center text-sm text-gray-500">
                  Didn't receive code?{' '}
                  <button
                    onClick={() => setStep('phone')}
                    className="text-primary-500 font-medium hover:underline"
                  >
                    Resend
                  </button>
                </p>

                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-xl text-sm text-yellow-800">
                  <strong>Dev Mode:</strong> Use OTP <span className="font-mono font-bold">123456</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
