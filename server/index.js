const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Basic API routes for testing
app.get('/', (req, res) => {
  res.json({ message: 'AI Graffiti Wall Server is running!' });
});

app.get('/api/status', (req, res) => {
  res.json({ 
    status: 'running', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Data storage (file-based for simplicity)
const dataDir = path.join(__dirname, 'data');
const galleryFile = path.join(dataDir, 'gallery.json');

// Initialize data directory and gallery file
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

if (!fs.existsSync(galleryFile)) {
  fs.writeFileSync(galleryFile, JSON.stringify([]));
}

// Gallery management
function loadGallery() {
  try {
    return JSON.parse(fs.readFileSync(galleryFile, 'utf8'));
  } catch (error) {
    return [];
  }
}

function saveGallery(gallery) {
  // Keep only last 50 artworks
  const limitedGallery = gallery.slice(-50);
  fs.writeFileSync(galleryFile, JSON.stringify(limitedGallery, null, 2));
  return limitedGallery;
}

// Simple gallery API routes
app.get('/api/gallery', (req, res) => {
  try {
    const gallery = loadGallery();
    gallery.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    res.json(gallery);
  } catch (error) {
    console.error('Error fetching gallery:', error);
    res.status(500).json({ error: 'Failed to fetch gallery' });
  }
});

app.post('/api/gallery', (req, res) => {
  try {
    const { image, nickname, timestamp } = req.body;
    
    if (!image) {
      return res.status(400).json({ error: 'Image data is required' });
    }
    
    const gallery = loadGallery();
    const newArtwork = {
      id: Date.now().toString(),
      image,
      nickname: nickname || 'Anonymous',
      timestamp: timestamp || new Date().toISOString(),
    };
    
    gallery.push(newArtwork);
    saveGallery(gallery);
    
    // Broadcast to display screens
    io.emit('artwork:display', newArtwork);
    
    res.status(201).json(newArtwork);
  } catch (error) {
    console.error('Error adding artwork:', error);
    res.status(500).json({ error: 'Failed to add artwork' });
  }
});

app.delete('/api/gallery/:id', (req, res) => {
  try {
    const gallery = loadGallery();
    const filteredGallery = gallery.filter(art => art.id !== req.params.id);
    
    if (gallery.length === filteredGallery.length) {
      return res.status(404).json({ error: 'Artwork not found' });
    }
    
    saveGallery(filteredGallery);
    res.json({ success: true, message: 'Artwork deleted successfully' });
  } catch (error) {
    console.error('Error deleting artwork:', error);
    res.status(500).json({ error: 'Failed to delete artwork' });
  }
});

// Socket.IO events
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);
  
  // Send current gallery to new display connections
  socket.on('display:connect', () => {
    const gallery = loadGallery();
    socket.emit('gallery:update', gallery);
  });
  
  // Artwork submission
  socket.on('artwork:submit', (data) => {
    const gallery = loadGallery();
    const newArtwork = {
      id: Date.now().toString(),
      ...data,
      timestamp: new Date().toISOString()
    };
    gallery.push(newArtwork);
    saveGallery(gallery);
    
    // Broadcast to all display screens
    io.emit('artwork:display', newArtwork);
    
    // Acknowledge submission
    socket.emit('artwork:submitted', { success: true, id: newArtwork.id });
  });
  
  // Admin controls
  socket.on('display:clear', () => {
    io.emit('display:clear');
  });
  
  socket.on('artwork:delete', (artworkId) => {
    const gallery = loadGallery();
    const filteredGallery = gallery.filter(artwork => artwork.id !== artworkId);
    saveGallery(filteredGallery);
    io.emit('gallery:update', filteredGallery);
  });
  
  // Timer events
  socket.on('timer:start', (duration) => {
    io.emit('timer:start', duration);
  });
  
  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`AI Graffiti Wall server running on port ${PORT}`);
  console.log(`API Status: http://localhost:${PORT}/api/status`);
  console.log(`Gallery API: http://localhost:${PORT}/api/gallery`);
});
