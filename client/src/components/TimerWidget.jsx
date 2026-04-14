import { useState, useEffect, useRef } from 'react';

const TimerWidget = ({ duration, onTimeUp, isActive }) => {
  const [timeLeft, setTimeLeft] = useState(duration);
  const [isRunning, setIsRunning] = useState(isActive);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prevTime) => {
          if (prevTime <= 1) {
            setIsRunning(false);
            onTimeUp?.();
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, timeLeft, onTimeUp]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const resetTimer = () => {
    setTimeLeft(duration);
    setIsRunning(true);
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const progress = ((duration - timeLeft) / duration) * 100;
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="fixed top-4 right-4 z-10">
      <div className="relative w-24 h-24">
        {/* Circular Progress */}
        <svg className="transform -rotate-90 w-24 h-24">
          <circle
            cx="48"
            cy="48"
            r="45"
            stroke="#374151"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="48"
            cy="48"
            r="45"
            stroke="#39ff14"
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-linear"
          />
        </svg>
        
        {/* Timer Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-green-400 font-bold text-lg font-mono">
            {formatTime(timeLeft)}
          </span>
          <span className="text-gray-400 text-xs">Time Left</span>
        </div>
      </div>

      {/* Timer Controls */}
      <div className="flex space-x-1 mt-2">
        <button
          onClick={toggleTimer}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs px-2 py-1 rounded"
        >
          {isRunning ? 'Pause' : 'Start'}
        </button>
        <button
          onClick={resetTimer}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-xs px-2 py-1 rounded"
        >
          Reset
        </button>
      </div>

      {/* Warning when time is low */}
      {timeLeft <= 30 && timeLeft > 0 && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
          <div className="bg-red-600 text-white text-xs px-2 py-1 rounded animate-pulse">
            {timeLeft <= 10 ? 'Time almost up!' : '30 seconds left!'}
          </div>
        </div>
      )}
    </div>
  );
};

export default TimerWidget;
