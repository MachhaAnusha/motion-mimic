import express from 'express';
import axios from 'axios';

const router = express.Router();

// Replicate API for AI image generation
router.post('/generate-graffiti', async (req, res) => {
  try {
    const { text, style, width = 512, height = 512 } = req.body;

    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }

    // Style-specific prompts for graffiti generation
    const stylePrompts = {
      bubble: 'bubble graffiti style, colorful street art, bold rounded letters, vibrant colors',
      wildstyle: 'wildstyle graffiti, complex interlocking letters, street art masterpiece, urban art',
      block: 'block letter graffiti, bold street art, urban typography, clean lines',
      tag: 'graffiti tag style, signature street art, handwritten urban lettering',
      stencil: 'stencil graffiti style, clean cut-out letters, street art stencil design',
    };

    const prompt = `${stylePrompts[style] || stylePrompts.bubble}, text "${text}", high quality, detailed, no background`;

    // Call Replicate API
    const response = await axios.post('https://api.replicate.com/v1/predictions', {
      version: 'ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4', // Stable Diffusion model
      input: {
        prompt: prompt,
        width: width,
        height: height,
        num_outputs: 1,
        num_inference_steps: 20,
        guidance_scale: 7.5,
      },
    }, {
      headers: {
        'Authorization': `Token ${process.env.REPLICATE_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    const prediction = response.data;

    // Poll for completion
    let imageUrl = null;
    let attempts = 0;
    const maxAttempts = 30;

    while (!imageUrl && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds

      const statusResponse = await axios.get(`https://api.replicate.com/v1/predictions/${prediction.id}`, {
        headers: {
          'Authorization': `Token ${process.env.REPLICATE_API_KEY}`,
        },
      });

      const status = statusResponse.data;

      if (status.status === 'succeeded') {
        imageUrl = status.output[0];
        break;
      } else if (status.status === 'failed') {
        throw new Error('Image generation failed');
      }

      attempts++;
    }

    if (!imageUrl) {
      throw new Error('Image generation timed out');
    }

    res.json({ imageUrl, text, style });

  } catch (error) {
    console.error('Error generating graffiti:', error);
    res.status(500).json({ error: 'Failed to generate graffiti image' });
  }
});

// AI image enhancement using img2img
router.post('/enhance-image', async (req, res) => {
  try {
    const { imageUrl, style, strength = 0.7 } = req.body;

    if (!imageUrl) {
      return res.status(400).json({ error: 'Image URL is required' });
    }

    // Style-specific enhancement prompts
    const stylePrompts = {
      'Old School NYC': 'classic NYC graffiti style, 1980s street art, urban aesthetic',
      'Wildstyle': 'wildstyle graffiti enhancement, complex street art, urban masterpiece',
      'Japanese Kanji': 'Japanese street art style, kanji graffiti, urban calligraphy',
      'Psychedelic': 'psychedelic graffiti art, vibrant colors, trippy street art',
      'Stencil Art': 'stencil graffiti style, clean lines, urban stencil design',
      'Mural': 'large scale mural style, professional street art, urban masterpiece',
    };

    const prompt = stylePrompts[style] || stylePrompts['Old School NYC'];

    // Call Replicate API for img2img
    const response = await axios.post('https://api.replicate.com/v1/predictions', {
      version: '435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117', // img2img model
      input: {
        prompt: prompt,
        image: imageUrl,
        strength: strength,
        num_outputs: 1,
        num_inference_steps: 20,
        guidance_scale: 7.5,
      },
    }, {
      headers: {
        'Authorization': `Token ${process.env.REPLICATE_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    const prediction = response.data;

    // Poll for completion
    let enhancedImageUrl = null;
    let attempts = 0;
    const maxAttempts = 30;

    while (!enhancedImageUrl && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds

      const statusResponse = await axios.get(`https://api.replicate.com/v1/predictions/${prediction.id}`, {
        headers: {
          'Authorization': `Token ${process.env.REPLICATE_API_KEY}`,
        },
      });

      const status = statusResponse.data;

      if (status.status === 'succeeded') {
        enhancedImageUrl = status.output[0];
        break;
      } else if (status.status === 'failed') {
        throw new Error('Image enhancement failed');
      }

      attempts++;
    }

    if (!enhancedImageUrl) {
      throw new Error('Image enhancement timed out');
    }

    res.json({ enhancedImageUrl, style });

  } catch (error) {
    console.error('Error enhancing image:', error);
    res.status(500).json({ error: 'Failed to enhance image' });
  }
});

export default router;
