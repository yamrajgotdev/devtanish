import { useState, useRef, useEffect } from 'react';

export default function BottomSheetPanel({ isOpen, onClose, children, title }) {
  const [dragY, setDragY] = useState(0);
  const [height, setHeight] = useState(300);
  const [isExpanded, setIsExpanded] = useState(false);
  const startY = useRef(0);
  const sheetRef = useRef(null);

  useEffect(() => {
    if (sheetRef.current) {
      setHeight(sheetRef.current.offsetHeight);
    }
  }, [isOpen]);

  const handleTouchStart = (e) => {
    startY.current = e.touches[0].clientY;
  };

  const handleTouchMove = (e) => {
    const delta = e.touches[0].clientY - startY.current;
    if (delta > 0) {
      setDragY(delta);
    }
  };

  const handleTouchEnd = () => {
    if (dragY > 100) {
      onClose();
    }
    setDragY(0);
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      
      <div
        ref={sheetRef}
        style={{
          transform: `translateY(${Math.max(0, dragY)}px)`,
          height: isExpanded ? '70vh' : 'auto',
        }}
        className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl pointer-events-auto transition-all duration-300 max-h-[85vh] overflow-hidden"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div className="flex justify-center pt-3 pb-2">
          <button
            onClick={toggleExpand}
            className="w-12 h-1.5 bg-gray-300 rounded-full"
          />
        </div>
        
        {title && (
          <div className="px-4 py-2 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-800">{title}</h2>
          </div>
        )}
        
        <div className="p-4 overflow-y-auto max-h-[70vh] pb-safe">
          {children}
        </div>
      </div>
    </div>
  );
}
