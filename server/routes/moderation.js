import express from 'express';
import axios from 'axios';

const router = express.Router();

// Simple profanity filter
const PROFANE_WORDS = [
  'damn', 'hell', 'shit', 'fuck', 'bitch', 'ass', 'crap', 'piss'
];

const checkProfanity = (text) => {
  const lowerText = text.toLowerCase();
  return PROFANE_WORDS.some(word => lowerText.includes(word));
};

// Text moderation endpoint
router.post('/text', async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    // First check local profanity filter
    if (checkProfanity(text)) {
      return res.json({ 
        appropriate: false, 
        reason: 'Local profanity filter',
        flaggedWords: PROFANE_WORDS.filter(word => text.toLowerCase().includes(word))
      });
    }

    // Then check with OpenAI Moderation API
    const response = await axios.post('https://api.openai.com/v1/moderations', {
      input: text,
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    const result = response.data;
    const flagged = result.results[0]?.flagged || false;
    const categories = result.results[0]?.categories || {};
    const categoryScores = result.results[0]?.category_scores || {};

    if (flagged) {
      const flaggedCategories = Object.entries(categories)
        .filter(([_, flagged]) => flagged)
        .map(([category, _]) => category);

      return res.json({
        appropriate: false,
        reason: 'OpenAI moderation',
        flaggedCategories,
        categoryScores,
      });
    }

    res.json({ appropriate: true });

  } catch (error) {
    console.error('Text moderation error:', error);
    res.status(500).json({ error: 'Failed to moderate text' });
  }
});

// Image moderation endpoint
router.post('/image', async (req, res) => {
  try {
    const { imageData } = req.body;

    if (!imageData) {
      return res.status(400).json({ error: 'Image data is required' });
    }

    // Convert data URL to base64 if needed
    const base64Data = imageData.startsWith('data:') 
      ? imageData.split(',')[1] 
      : imageData;

    // Use Google Vision SafeSearch API
    const response = await axios.post(`https://vision.googleapis.com/v1/images:annotate?key=${process.env.GOOGLE_VISION_API_KEY}`, {
      requests: [
        {
          image: {
            content: base64Data,
          },
          features: [
            {
              type: 'SAFE_SEARCH_DETECTION',
              maxResults: 1,
            },
            {
              type: 'LABEL_DETECTION',
              maxResults: 10,
            },
          ],
        },
      ],
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const result = response.data;
    const safeSearch = result.responses[0]?.safeSearchAnnotation;
    const labels = result.responses[0]?.labelAnnotations || [];

    if (!safeSearch) {
      return res.json({
        appropriate: false,
        reason: 'No safe search results returned',
      });
    }

    // Define acceptable thresholds
    const acceptableLevels = ['VERY_UNLIKELY', 'UNLIKELY'];
    const restrictedCategories = ['adult', 'violence', 'racy'];

    const inappropriateCategories = Object.entries(safeSearch)
      .filter(([category, level]) => 
        restrictedCategories.includes(category) && !acceptableLevels.includes(level)
      )
      .map(([category, level]) => ({ category, level }));

    // Additional label-based filtering
    const problematicLabels = labels
      .filter(label => {
        const problematicKeywords = [
          'weapon', 'gun', 'knife', 'blood', 'violence', 'adult', 'nude',
          'sexual', 'drugs', 'alcohol', 'tobacco', 'hate', 'racist'
        ];
        return problematicKeywords.some(keyword => 
          label.description.toLowerCase().includes(keyword)
        );
      })
      .map(label => label.description);

    const isAppropriate = inappropriateCategories.length === 0 && problematicLabels.length === 0;

    if (!isAppropriate) {
      return res.json({
        appropriate: false,
        reason: 'Inappropriate content detected',
        safeSearchIssues: inappropriateCategories,
        problematicLabels,
      });
    }

    res.json({ 
      appropriate: true,
      safeSearch,
      labels: labels.slice(0, 5), // Return top 5 labels for context
    });

  } catch (error) {
    console.error('Image moderation error:', error);
    res.status(500).json({ error: 'Failed to moderate image' });
  }
});

// Get moderation statistics
router.get('/stats', async (req, res) => {
  try {
    // In a real implementation, this would query a database
    // For now, return mock data
    res.json({
      totalTextModerations: 0,
      totalImageModerations: 0,
      blockedTexts: 0,
      blockedImages: 0,
      averageResponseTime: 0,
    });
  } catch (error) {
    console.error('Error fetching moderation stats:', error);
    res.status(500).json({ error: 'Failed to fetch moderation statistics' });
  }
});

export default router;
