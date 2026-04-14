import { useState } from 'react';

// Profanity filter list (simplified version)
const PROFANE_WORDS = [
  'damn', 'hell', 'shit', 'fuck', 'bitch', 'ass', 'crap', 'piss',
  // Add more words as needed
];

export const useModeration = () => {
  const [moderationLog, setModerationLog] = useState([]);

  const addToLog = (message) => {
    setModerationLog(prev => [
      { message, timestamp: new Date().toISOString() },
      ...prev.slice(0, 99) // Keep last 100 entries
    ]);
  };

  // Local profanity filter
  const checkProfanity = (text) => {
    const lowerText = text.toLowerCase();
    return PROFANE_WORDS.some(word => lowerText.includes(word));
  };

  // Text moderation using OpenAI API
  const moderateText = async (text) => {
    try {
      // First, check local profanity filter
      if (checkProfanity(text)) {
        addToLog(`Text blocked by local filter: "${text}"`);
        return false;
      }

      // Then check with OpenAI Moderation API
      const response = await fetch('https://api.openai.com/v1/moderations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          input: text,
        }),
      });

      if (!response.ok) {
        console.error('OpenAI moderation API error:', response.statusText);
        addToLog(`OpenAI moderation API error: ${response.statusText}`);
        return false;
      }

      const result = await response.json();
      const flagged = result.results[0]?.flagged || false;

      if (flagged) {
        addToLog(`Text flagged by OpenAI: "${text}"`);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error moderating text:', error);
      addToLog(`Text moderation error: ${error.message}`);
      // Fail safe - if moderation fails, allow the content
      return true;
    }
  };

  // Image moderation using Google Vision SafeSearch API
  const moderateImage = async (imageDataUrl) => {
    try {
      // Convert data URL to base64
      const base64Data = imageDataUrl.split(',')[1];

      const response = await fetch(`https://vision.googleapis.com/v1/images:annotate?key=${import.meta.env.VITE_GOOGLE_VISION_API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
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
              ],
            },
          ],
        }),
      });

      if (!response.ok) {
        console.error('Google Vision API error:', response.statusText);
        addToLog(`Google Vision API error: ${response.statusText}`);
        return false;
      }

      const result = await response.json();
      const safeSearch = result.responses[0]?.safeSearchAnnotation;

      if (!safeSearch) {
        addToLog('No safe search results returned');
        return false;
      }

      // Check for inappropriate content
      const inappropriateCategories = [
        'adult', 'spoof', 'medical', 'violence', 'racy'
      ];

      const isAppropriate = inappropriateCategories.every(category => {
        const likelihood = safeSearch[category];
        return likelihood === 'VERY_UNLIKELY' || likelihood === 'UNLIKELY';
      });

      if (!isAppropriate) {
        addToLog(`Image flagged by safe search: ${JSON.stringify(safeSearch)}`);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Error moderating image:', error);
      addToLog(`Image moderation error: ${error.message}`);
      // Fail safe - if moderation fails, allow the content
      return true;
    }
  };

  // Canvas snapshot moderation
  const moderateCanvasSnapshot = async (canvas) => {
    if (!canvas) return true;

    try {
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      return await moderateImage(imageDataUrl);
    } catch (error) {
      console.error('Error moderating canvas snapshot:', error);
      addToLog(`Canvas snapshot moderation error: ${error.message}`);
      return true;
    }
  };

  return {
    moderateText,
    moderateImage,
    moderateCanvasSnapshot,
    moderationLog,
    addToLog,
  };
};
