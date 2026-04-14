import { useState } from 'react';

export default function OTPInput({ length = 6, onComplete }) {
  const [otp, setOtp] = useState('');

  const handleChange = (value, index) => {
    const newOtp = otp.split('');
    newOtp[index] = value;
    const updated = newOtp.join('');
    setOtp(updated);

    if (value && index < length - 1) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }

    if (updated.length === length) {
      onComplete(updated);
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`otp-${index - 1}`)?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, length);
    setOtp(pastedData);
    if (pastedData.length === length) {
      onComplete(pastedData);
    }
  };

  return (
    <div className="flex justify-center gap-2" onPaste={handlePaste}>
      {Array.from({ length }).map((_, i) => (
        <input
          key={i}
          id={`otp-${i}`}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={otp[i] || ''}
          onChange={(e) => handleChange(e.target.value, i)}
          onKeyDown={(e) => handleKeyDown(e, i)}
          className="w-12 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-xl focus:border-primary-500 focus:outline-none transition-colors"
        />
      ))}
    </div>
  );
}
