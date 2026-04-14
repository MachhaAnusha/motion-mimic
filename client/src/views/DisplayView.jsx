import { useState, useEffect, useRef } from 'react';
import QRCode from 'qrcode';
import { useSocket } from '../hooks/useSocket';

const DisplayView = () => {
  const [currentArtwork, setCurrentArtwork] = useState(null);
  const [gallery, setGallery] = useState([]);
  const [isGalleryMode, setIsGalleryMode] = useState(false);
  const [currentGalleryIndex, setCurrentGalleryIndex] = useState(0);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [showQR, setShowQR] = useState(true);
  const canvasRef = useRef(null);
  const galleryIntervalRef = useRef(null);

  const socket = useSocket();

  // Generate QR code for creator view
  useEffect(() => {
    const generateQR = async () => {
      try {
        const url = window.location.origin + '/create';
        const qr = await QRCode.toDataURL(url, {
          width: 150,
          margin: 1,
          color: {
            dark: '#39ff14',
            light: '#000000',
          },
        });
        setQrCodeUrl(qr);
      } catch (err) {
        console.error('Error generating QR code:', err);
      }
    };
    generateQR();
  }, []);

  // Handle socket events
  useEffect(() => {
    if (!socket) return;

    // Handle new artwork submission
    socket.on('artwork:display', (artwork) => {
      setCurrentArtwork(artwork);
      setIsGalleryMode(false);
      setShowQR(false);
      
      // Hide QR for 10 seconds when new artwork arrives
      setTimeout(() => {
        setShowQR(true);
      }, 10000);
    });

    // Handle gallery updates
    socket.on('gallery:update', (updatedGallery) => {
      setGallery(updatedGallery);
    });

    // Handle display clear
    socket.on('display:clear', () => {
      setCurrentArtwork(null);
      setIsGalleryMode(false);
    });

    // Request gallery on connect
    socket.emit('display:connect');

    return () => {
      socket.off('artwork:display');
      socket.off('gallery:update');
      socket.off('display:clear');
    };
  }, [socket]);

  // Gallery mode slideshow
  useEffect(() => {
    if (isGalleryMode && gallery.length > 0) {
      galleryIntervalRef.current = setInterval(() => {
        setCurrentGalleryIndex((prevIndex) => {
          const nextIndex = (prevIndex + 1) % gallery.length;
          setCurrentArtwork(gallery[nextIndex]);
          return nextIndex;
        });
      }, 30000); // Change every 30 seconds
    } else {
      if (galleryIntervalRef.current) {
        clearInterval(galleryIntervalRef.current);
      }
    }

    return () => {
      if (galleryIntervalRef.current) {
        clearInterval(galleryIntervalRef.current);
      }
    };
  }, [isGalleryMode, gallery]);

  // Auto-enter gallery mode when idle
  useEffect(() => {
    const idleTimer = setTimeout(() => {
      if (gallery.length > 0 && !isGalleryMode) {
        setIsGalleryMode(true);
        setCurrentGalleryIndex(0);
        setCurrentArtwork(gallery[0]);
      }
    }, 30000); // Enter gallery mode after 30 seconds of inactivity

    return () => clearTimeout(idleTimer);
  }, [currentArtwork, gallery, isGalleryMode]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e) => {
      switch (e.key.toLowerCase()) {
        case 'f':
          // Toggle fullscreen
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
          } else {
            document.exitFullscreen();
          }
          break;
        case 'n':
          // Next artwork in gallery
          if (gallery.length > 0) {
            const nextIndex = (currentGalleryIndex + 1) % gallery.length;
            setCurrentGalleryIndex(nextIndex);
            setCurrentArtwork(gallery[nextIndex]);
            setIsGalleryMode(true);
          }
          break;
        case 'g':
          // Toggle gallery mode
          if (gallery.length > 0) {
            setIsGalleryMode(!isGalleryMode);
            if (!isGalleryMode) {
              setCurrentGalleryIndex(0);
              setCurrentArtwork(gallery[0]);
            }
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [gallery, currentGalleryIndex, isGalleryMode]);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background particles effect */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-10 left-10 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        <div className="absolute top-20 right-20 w-3 h-3 bg-pink-400 rounded-full animate-pulse delay-75"></div>
        <div className="absolute bottom-20 left-20 w-2 h-2 bg-blue-400 rounded-full animate-pulse delay-150"></div>
        <div className="absolute bottom-10 right-10 w-4 h-4 bg-yellow-400 rounded-full animate-pulse delay-300"></div>
      </div>

      {/* Main Display Area */}
      <div className="relative w-full h-full flex items-center justify-center p-8">
        {currentArtwork ? (
          <div className="relative max-w-full max-h-full">
            {/* Artwork Image */}
            <img
              src={currentArtwork.image}
              alt="Graffiti artwork"
              className="max-w-full max-h-full object-contain spray-reveal"
              style={{
                maxHeight: 'calc(100vh - 200px)',
                maxWidth: 'calc(100vw - 100px)',
              }}
            />
            
            {/* Artwork Info */}
            <div className="absolute bottom-4 left-4 right-4 text-center">
              <div className="inline-block bg-black bg-opacity-75 rounded-lg px-4 py-2 backdrop-blur-sm">
                <p className="text-green-400 font-graffiti text-lg">
                  {currentArtwork.nickname || 'Anonymous'}
                </p>
                <p className="text-gray-400 text-sm">
                  {formatTimestamp(currentArtwork.timestamp)}
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Idle Screen */
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-green-400 font-graffiti neon-glow mb-8">
              AI Graffiti Wall
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 mb-12">
              Scan the QR code to create your masterpiece!
            </p>
            
            {qrCodeUrl && (
              <div className="inline-block bg-white p-4 rounded-lg">
                <img src={qrCodeUrl} alt="QR Code" className="w-32 h-32" />
              </div>
            )}
            
            <p className="text-gray-500 mt-4 text-sm">
              Press F for fullscreen • N for next artwork • G for gallery mode
            </p>
          </div>
        )}
      </div>

      {/* QR Code Overlay */}
      {showQR && qrCodeUrl && !currentArtwork && (
        <div className="absolute top-4 right-4 bg-black bg-opacity-75 p-3 rounded-lg backdrop-blur-sm">
          <img src={qrCodeUrl} alt="Create QR Code" className="w-20 h-20" />
          <p className="text-xs text-green-400 mt-1 text-center">Create</p>
        </div>
      )}

      {/* Gallery Mode Indicator */}
      {isGalleryMode && (
        <div className="absolute top-4 left-4 bg-black bg-opacity-75 px-3 py-2 rounded-lg backdrop-blur-sm">
          <p className="text-green-400 text-sm font-graffiti">
            Gallery Mode ({currentGalleryIndex + 1}/{gallery.length})
          </p>
        </div>
      )}

      {/* Controls Hint */}
      <div className="absolute bottom-4 right-4 text-xs text-gray-600">
        F: Fullscreen | N: Next | G: Gallery
      </div>

      {/* Loading State */}
      {!currentArtwork && gallery.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p className="text-gray-400">Waiting for artwork...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DisplayView;
