# AI Graffiti Wall 🎨

A full-stack AI-powered interactive graffiti wall web application designed for public events and installations. Create digital graffiti artwork with AI enhancement and real-time display synchronization.

## Features

### 🎨 Creator View (`/create`)
- Full drawing canvas with 16:9 aspect ratio
- Multiple brush types (Freehand, Spray, Marker, Chalk, Drip, Eraser)
- Color picker with graffiti palettes and neon glow effects
- Background textures (Brick, Concrete, Metal, Wood, etc.)
- Text-to-graffiti AI generation
- AI drawing enhancement and style transfer
- Touch-friendly for phones, tablets, and desktop
- Session timer with countdown
- Download and share functionality

### 🖼️ Display View (`/display`)
- Full-screen artwork display
- Real-time synchronization via Socket.IO
- Animated spray-paint reveal effects
- Gallery slideshow mode (auto-rotates when idle)
- QR code for audience participation
- Keyboard controls (F: fullscreen, N: next, G: gallery)

### ⚙️ Admin View (`/admin`)
- Password-protected admin panel
- Gallery management and moderation
- Display controls (clear, slideshow toggle)
- Session timer configuration
- Artwork statistics and analytics
- Content moderation log

### 🛡️ Multi-Layer Content Moderation
- **Text Moderation**: Local profanity filter + OpenAI API
- **Image Moderation**: Google Vision SafeSearch API
- **Canvas Snapshots**: Periodic content checking
- **Admin Override**: Manual content removal

## Tech Stack

- **Frontend**: React + Vite + TailwindCSS
- **Canvas**: Fabric.js for drawing functionality
- **Backend**: Node.js + Express
- **Real-time**: Socket.IO
- **AI Integration**: Replicate API (Stable Diffusion) + OpenAI API
- **Storage**: File-based JSON storage (easily upgradeable to database)

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-graffiti-wall
```

2. **Install server dependencies**
```bash
cd server
npm install
```

3. **Install client dependencies**
```bash
cd ../client
npm install
```

4. **Set up environment variables**

Create environment files with your API keys:

**Server** (`server/.env`):
```env
REPLICATE_API_KEY=your_replicate_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_VISION_API_KEY=your_google_vision_api_key_here
ADMIN_PASSWORD=your_admin_password
PORT=3000
```

**Client** (`client/.env`):
```env
VITE_SERVER_URL=http://localhost:3000
VITE_ADMIN_PASSWORD=admin123
```

### API Keys Setup

#### 1. Replicate API (for AI image generation)
1. Go to [Replicate](https://replicate.com/)
2. Sign up and verify your email
3. Navigate to your [API tokens page](https://replicate.com/account/api-tokens)
4. Create a new token
5. Copy the token and add it to `REPLICATE_API_KEY`

#### 2. OpenAI API (for text moderation)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to [API Keys](https://platform.openai.com/account/api-keys)
4. Create a new secret key
5. Copy the key and add it to `OPENAI_API_KEY`

#### 3. Google Vision API (for image moderation)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "Cloud Vision API"
4. Create credentials (API Key)
5. Copy the API key and add it to `GOOGLE_VISION_API_KEY`

### Running the Application

#### Option 1: Development Mode (Recommended)

1. **Start the server** (in `server/` directory):
```bash
npm run dev
```

2. **Start the client** (in `client/` directory):
```bash
npm run dev
```

3. **Access the application**:
- Creator View: http://localhost:5173/create
- Display View: http://localhost:5173/display  
- Admin View: http://localhost:5173/admin

#### Option 2: Production Mode

1. **Build the client** (in `client/` directory):
```bash
npm run build
```

2. **Start the server** (in `server/` directory):
```bash
npm start
```

3. **Access the application**:
- Creator View: http://localhost:3000/create
- Display View: http://localhost:3000/display
- Admin View: http://localhost:3000/admin

## Usage Guide

### For Event Setup

1. **Display Setup**:
   - Open `/display` on the projector or LED screen
   - Press `F` to enter fullscreen mode
   - The QR code will be visible for audience scanning

2. **Creator Devices**:
   - Participants scan QR code or go to `/create`
   - Works on phones, tablets, and laptops
   - Touch-optimized for mobile devices

3. **Admin Monitoring**:
   - Access `/admin` with your admin password
   - Monitor submitted artwork
   - Remove inappropriate content
   - Control display settings

### Network Configuration

For multi-device usage on the same network:

1. **Find your local IP**:
```bash
# On Windows
ipconfig

# On Mac/Linux  
ifconfig
```

2. **Update client environment**:
```env
VITE_SERVER_URL=http://YOUR_LOCAL_IP:3000
```

3. **Connect devices**:
- All devices must be on the same WiFi network
- Use the local IP address instead of localhost
- Ensure firewall allows connections on port 3000

## Features in Detail

### Brush Types
- **Freehand**: Standard drawing brush
- **Spray**: Simulates aerosol spray paint effect
- **Marker**: Marker-like strokes
- **Chalk**: Chalk texture effect
- **Drip**: Paint drip effect
- **Eraser**: Remove drawn content

### Graffiti Styles
- **Bubble**: Rounded, bubbly letters
- **Wildstyle**: Complex, interlocking letters
- **Block**: Bold, square letters
- **Tag**: Quick, signature style
- **Stencil**: Clean, cut-out style

### Background Textures
- **Brick**: Classic brick wall texture
- **Concrete**: Urban concrete surface
- **Metal**: Industrial metal sheet
- **Wood**: Wooden plank texture
- **Black/White**: Solid colors

### AI Features
- **Text-to-Graffiti**: Convert text to styled graffiti
- **Style Transfer**: Apply artistic styles to drawings
- **Content Moderation**: Automated content filtering

## Troubleshooting

### Common Issues

1. **Socket Connection Issues**:
   - Check that server is running on port 3000
   - Verify firewall settings
   - Ensure correct VITE_SERVER_URL

2. **API Key Errors**:
   - Verify all API keys are correctly set
   - Check API key permissions and quotas
   - Ensure billing is set up for paid services

3. **Canvas Not Loading**:
   - Check browser console for errors
   - Ensure Fabric.js is loaded correctly
   - Try refreshing the page

4. **Mobile Issues**:
   - Enable touch events in browser settings
   - Check responsive design
   - Test on different mobile browsers

### Performance Tips

1. **For Large Events**:
   - Use a dedicated server
   - Consider Redis for Socket.IO scaling
   - Implement rate limiting

2. **Database Upgrade**:
   - Replace file storage with PostgreSQL/MongoDB
   - Add proper indexing
   - Implement backup strategy

## API Endpoints

### Gallery
- `GET /api/gallery` - Get all artworks
- `POST /api/gallery` - Add new artwork
- `DELETE /api/gallery/:id` - Delete artwork
- `GET /api/gallery/stats/summary` - Get statistics

### AI Services
- `POST /api/ai/generate-graffiti` - Generate graffiti text
- `POST /api/ai/enhance-image` - Enhance with AI

### Moderation
- `POST /api/moderation/text` - Moderate text content
- `POST /api/moderation/image` - Moderate image content

### Socket.IO Events
- `artwork:submit` - Submit new artwork
- `artwork:display` - Display artwork
- `artwork:delete` - Delete artwork
- `display:clear` - Clear display
- `gallery:update` - Update gallery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Created with ❤️ for interactive digital art experiences**
