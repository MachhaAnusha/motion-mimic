import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

const galleryFile = path.join(__dirname, '../data/gallery.json');

// Helper functions
function loadGallery() {
  try {
    if (!fs.existsSync(galleryFile)) {
      return [];
    }
    return JSON.parse(fs.readFileSync(galleryFile, 'utf8'));
  } catch (error) {
    console.error('Error loading gallery:', error);
    return [];
  }
}

function saveGallery(gallery) {
  try {
    // Keep only last 50 artworks
    const limitedGallery = gallery.slice(-50);
    fs.writeFileSync(galleryFile, JSON.stringify(limitedGallery, null, 2));
    return limitedGallery;
  } catch (error) {
    console.error('Error saving gallery:', error);
    throw error;
  }
}

// Get all artworks
router.get('/', (req, res) => {
  try {
    const gallery = loadGallery();
    // Sort by timestamp, newest first
    gallery.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    res.json(gallery);
  } catch (error) {
    console.error('Error fetching gallery:', error);
    res.status(500).json({ error: 'Failed to fetch gallery' });
  }
});

// Get single artwork by ID
router.get('/:id', (req, res) => {
  try {
    const gallery = loadGallery();
    const artwork = gallery.find(art => art.id === req.params.id);
    
    if (!artwork) {
      return res.status(404).json({ error: 'Artwork not found' });
    }
    
    res.json(artwork);
  } catch (error) {
    console.error('Error fetching artwork:', error);
    res.status(500).json({ error: 'Failed to fetch artwork' });
  }
});

// Add new artwork
router.post('/', (req, res) => {
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
      moderated: false,
    };
    
    gallery.push(newArtwork);
    saveGallery(gallery);
    
    res.status(201).json(newArtwork);
  } catch (error) {
    console.error('Error adding artwork:', error);
    res.status(500).json({ error: 'Failed to add artwork' });
  }
});

// Update artwork
router.put('/:id', (req, res) => {
  try {
    const gallery = loadGallery();
    const artworkIndex = gallery.findIndex(art => art.id === req.params.id);
    
    if (artworkIndex === -1) {
      return res.status(404).json({ error: 'Artwork not found' });
    }
    
    // Update artwork with new data
    gallery[artworkIndex] = { ...gallery[artworkIndex], ...req.body };
    saveGallery(gallery);
    
    res.json(gallery[artworkIndex]);
  } catch (error) {
    console.error('Error updating artwork:', error);
    res.status(500).json({ error: 'Failed to update artwork' });
  }
});

// Delete artwork
router.delete('/:id', (req, res) => {
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

// Get gallery statistics
router.get('/stats/summary', (req, res) => {
  try {
    const gallery = loadGallery();
    const totalArtworks = gallery.length;
    const uniqueArtists = [...new Set(gallery.map(art => art.nickname))].length;
    
    // Artworks in last 24 hours
    const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentArtworks = gallery.filter(art => new Date(art.timestamp) > last24Hours).length;
    
    // Most active artist
    const artistCounts = gallery.reduce((acc, art) => {
      acc[art.nickname] = (acc[art.nickname] || 0) + 1;
      return acc;
    }, {});
    
    const mostActiveArtist = Object.entries(artistCounts)
      .sort((a, b) => b[1] - a[1])[0];
    
    res.json({
      totalArtworks,
      uniqueArtists,
      recentArtworks,
      mostActiveArtist: mostActiveArtist ? { name: mostActiveArtist[0], count: mostActiveArtist[1] } : null,
      maxCapacity: 50,
      capacityUsed: Math.round((totalArtworks / 50) * 100),
    });
  } catch (error) {
    console.error('Error fetching gallery stats:', error);
    res.status(500).json({ error: 'Failed to fetch gallery statistics' });
  }
});

// Clear all artworks (admin only)
router.delete('/', (req, res) => {
  try {
    // In a real implementation, you'd check admin authentication here
    saveGallery([]);
    res.json({ success: true, message: 'Gallery cleared successfully' });
  } catch (error) {
    console.error('Error clearing gallery:', error);
    res.status(500).json({ error: 'Failed to clear gallery' });
  }
});

export default router;
