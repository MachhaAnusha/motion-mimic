import { useState, useEffect } from 'react';
import { useSocket } from '../hooks/useSocket';

const AdminView = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [gallery, setGallery] = useState([]);
  const [selectedArtwork, setSelectedArtwork] = useState(null);
  const [gallerySlideshow, setGallerySlideshow] = useState(true);
  const [sessionTimer, setSessionTimer] = useState(180);
  const [moderationLog, setModerationLog] = useState([]);
  const [loading, setLoading] = useState(false);

  const socket = useSocket();

  // Check authentication on mount
  useEffect(() => {
    const auth = localStorage.getItem('adminAuthenticated');
    if (auth === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  // Handle socket events
  useEffect(() => {
    if (!socket || !isAuthenticated) return;

    // Request initial gallery
    fetch('/api/gallery')
      .then(res => res.json())
      .then(data => setGallery(data))
      .catch(err => console.error('Error fetching gallery:', err));

    // Listen for gallery updates
    socket.on('gallery:update', setGallery);

    return () => {
      socket.off('gallery:update');
    };
  }, [socket, isAuthenticated]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === import.meta.env.VITE_ADMIN_PASSWORD || password === 'admin123') {
      setIsAuthenticated(true);
      localStorage.setItem('adminAuthenticated', 'true');
    } else {
      alert('Invalid password. Please try again.');
      setPassword('');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('adminAuthenticated');
  };

  const deleteArtwork = async (artworkId) => {
    if (!confirm('Are you sure you want to delete this artwork?')) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/gallery/${artworkId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setGallery(gallery.filter(artwork => artwork.id !== artworkId));
        if (selectedArtwork?.id === artworkId) {
          setSelectedArtwork(null);
        }
      } else {
        alert('Failed to delete artwork');
      }
    } catch (error) {
      console.error('Error deleting artwork:', error);
      alert('Error deleting artwork');
    } finally {
      setLoading(false);
    }
  };

  const clearDisplay = () => {
    socket?.emit('display:clear');
  };

  const pushToDisplay = (artwork) => {
    socket?.emit('artwork:display', artwork);
  };

  const toggleSlideshow = () => {
    setGallerySlideshow(!gallerySlideshow);
    // In a real implementation, this would control the display view
  };

  const updateTimer = () => {
    socket?.emit('timer:start', sessionTimer);
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="bg-gray-900 rounded-lg p-8 max-w-md w-full border-2 border-green-500">
          <h1 className="text-3xl font-bold text-green-400 mb-6 text-center font-graffiti">
            Admin Login
          </h1>
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label className="block text-white mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 rounded bg-gray-800 text-white border border-gray-700 focus:border-green-500 focus:outline-none"
                placeholder="Enter admin password"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-green-500 hover:bg-green-600 text-black font-bold py-3 px-6 rounded transition-colors"
            >
              Login
            </button>
          </form>
          <p className="text-gray-400 text-sm text-center mt-4">
            Default password: admin123 (change in production)
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-green-400 font-graffiti">
          Admin Panel
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition-colors"
        >
          Logout
        </button>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="toolbar p-4">
          <h3 className="text-lg font-bold mb-3 text-green-400">Display Controls</h3>
          <div className="space-y-2">
            <button
              onClick={clearDisplay}
              className="toolbar-button w-full bg-red-600 hover:bg-red-700"
            >
              Clear Display
            </button>
            <button
              onClick={() => toggleSlideshow()}
              className={`toolbar-button w-full ${gallerySlideshow ? 'bg-green-600' : 'bg-gray-600'}`}
            >
              Slideshow: {gallerySlideshow ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>

        <div className="toolbar p-4">
          <h3 className="text-lg font-bold mb-3 text-green-400">Session Timer</h3>
          <div className="space-y-2">
            <input
              type="number"
              value={sessionTimer}
              onChange={(e) => setSessionTimer(parseInt(e.target.value) || 180)}
              className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
              min="30"
              max="600"
              step="30"
            />
            <button
              onClick={updateTimer}
              className="toolbar-button w-full bg-blue-600 hover:bg-blue-700"
            >
              Update Timer ({Math.floor(sessionTimer / 60)}:{(sessionTimer % 60).toString().padStart(2, '0')})
            </button>
          </div>
        </div>

        <div className="toolbar p-4">
          <h3 className="text-lg font-bold mb-3 text-green-400">Statistics</h3>
          <div className="space-y-1 text-sm">
            <p>Total Artworks: {gallery.length}</p>
            <p>Gallery Capacity: 50</p>
            <p>Storage Used: {Math.round((gallery.length / 50) * 100)}%</p>
          </div>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gallery List */}
        <div className="toolbar p-4">
          <h3 className="text-lg font-bold mb-3 text-green-400">Gallery ({gallery.length})</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {gallery.map((artwork) => (
              <div
                key={artwork.id}
                className={`flex items-center space-x-3 p-2 rounded cursor-pointer transition-colors ${
                  selectedArtwork?.id === artwork.id ? 'bg-gray-700' : 'hover:bg-gray-800'
                }`}
                onClick={() => setSelectedArtwork(artwork)}
              >
                <img
                  src={artwork.image}
                  alt={artwork.nickname}
                  className="w-16 h-12 object-cover rounded"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{artwork.nickname}</p>
                  <p className="text-xs text-gray-400">{formatTimestamp(artwork.timestamp)}</p>
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      pushToDisplay(artwork);
                    }}
                    className="toolbar-button text-xs px-2 py-1 bg-green-600 hover:bg-green-700"
                  >
                    Show
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteArtwork(artwork.id);
                    }}
                    className="toolbar-button text-xs px-2 py-1 bg-red-600 hover:bg-red-700"
                    disabled={loading}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
            {gallery.length === 0 && (
              <p className="text-gray-500 text-center py-8">No artworks in gallery yet</p>
            )}
          </div>
        </div>

        {/* Selected Artwork Preview */}
        <div className="toolbar p-4">
          <h3 className="text-lg font-bold mb-3 text-green-400">Preview</h3>
          {selectedArtwork ? (
            <div className="space-y-4">
              <img
                src={selectedArtwork.image}
                alt={selectedArtwork.nickname}
                className="w-full rounded-lg max-h-64 object-contain bg-gray-800"
              />
              <div className="space-y-2 text-sm">
                <p><strong>Artist:</strong> {selectedArtwork.nickname}</p>
                <p><strong>Created:</strong> {formatTimestamp(selectedArtwork.timestamp)}</p>
                <p><strong>ID:</strong> {selectedArtwork.id}</p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => pushToDisplay(selectedArtwork)}
                  className="toolbar-button flex-1 bg-green-600 hover:bg-green-700"
                >
                  Push to Display
                </button>
                <button
                  onClick={() => deleteArtwork(selectedArtwork.id)}
                  className="toolbar-button flex-1 bg-red-600 hover:bg-red-700"
                  disabled={loading}
                >
                  Delete
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Select an artwork to preview
            </div>
          )}
        </div>
      </div>

      {/* Moderation Log */}
      <div className="toolbar p-4 mt-6">
        <h3 className="text-lg font-bold mb-3 text-green-400">Moderation Log</h3>
        <div className="space-y-2 max-h-32 overflow-y-auto">
          {moderationLog.length > 0 ? (
            moderationLog.map((log, index) => (
              <div key={index} className="text-sm text-gray-400">
                <span className="text-gray-500">{formatTimestamp(log.timestamp)}</span> - {log.message}
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No moderation actions yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminView;
