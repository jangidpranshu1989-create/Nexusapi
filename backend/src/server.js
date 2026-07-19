const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const archiver = require('archiver');
const { body, validationResult } = require('express-validator');
const { v4: uuidv4 } = require('uuid');
const os = require('os');

const app = express();
const PORT = 3000;
const currentUser = os.userInfo().username;

app.use(cors());
app.use(express.json());

const pool = new Pool({
  host: 'localhost',
  database: 'nexusapi',
  user: currentUser,
  password: 'postgres',
  port: 5432,
});

// Virtual file system for downloads
const systemFiles = {
  'universal-file-converter': {
    'src/convert.py': `import subprocess
from fastapi import FastAPI, UploadFile

app = FastAPI()

@app.post("/convert")
async def convert_file(file: UploadFile, target_format: str):
    # FFmpeg based conversion
    input_path = f"/tmp/input.{file.filename.split('.')[-1]}"
    output_path = f"/tmp/output.{target_format}"
    
    with open(input_path, "wb") as f:
        f.write(await file.read())
    
    subprocess.run(["ffmpeg", "-i", input_path, output_path])
    return {"message": "File converted successfully"}
`,
    'requirements.txt': `fastapi==0.104.1
python-multipart==0.0.6
uvicorn==0.24.0
ffmpeg-python==0.2.0
`,
    'config.py': `import os

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"))
SUPPORTED_FORMATS = ["mp4", "avi", "mkv", "mp3", "wav", "pdf", "docx"]
`,
    'README.md': `# Universal File Converter API

Convert between 50+ file formats instantly using FFmpeg and Python.

## 🚀 Quick Start

\`\`\`bash
pip install -r requirements.txt
uvicorn src.convert:app --reload --port 8000
\`\`\`

## 📡 API Endpoints

- POST /convert - Upload and convert files

## 🔧 Environment Variables

- UPLOAD_DIR - Upload directory path
- MAX_FILE_SIZE - Maximum file size in bytes
- SUPPORTED_FORMATS - Comma-separated format list
`
  },
  'jwt-authentication-system': {
    'src/auth.js': `const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const JWT_SECRET = process.env.JWT_SECRET || 'nexusapi-secret-key';
const JWT_EXPIRY = '24h';

module.exports = {
  generateToken: (user) => {
    return jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRY }
    );
  },

  verifyToken: (token) => {
    return jwt.verify(token, JWT_SECRET);
  },

  hashPassword: async (password) => {
    return await bcrypt.hash(password, 10);
  },

  comparePassword: async (password, hash) => {
    return await bcrypt.compare(password, hash);
  }
};
`,
    'src/routes/auth.js': `const router = require('express').Router();
const { generateToken, comparePassword } = require('../auth');
const pool = require('../db');

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const user = result.rows[0];
    const validPassword = await comparePassword(password, user.password_hash);
    
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = generateToken(user);
    res.json({ token, user: { id: user.id, email: user.email, name: user.name } });
  } catch (err) {
    res.status(500).json({ error: 'Login failed' });
  }
});

router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;
    const { hashPassword } = require('../auth');
    const hashedPassword = await hashPassword(password);
    
    const result = await pool.query(
      'INSERT INTO users (email, password_hash, name) VALUES ($1, $2, $3) RETURNING id, email, name',
      [email, hashedPassword, name]
    );
    
    const user = result.rows[0];
    const token = generateToken(user);
    res.status(201).json({ token, user });
  } catch (err) {
    res.status(500).json({ error: 'Registration failed' });
  }
});

module.exports = router;
`,
    'package.json': `{
  "name": "jwt-auth-system",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "bcrypt": "^5.1.1",
    "pg": "^8.11.3",
    "dotenv": "^16.3.1"
  }
}
`,
    'README.md': `# JWT Authentication System

Complete authentication boilerplate for Node.js with Express and PostgreSQL.

## 🚀 Quick Start

\`\`\`bash
npm install
cp .env.example .env
npm start
\`\`\`

## 📡 API Endpoints

- POST /api/auth/login - User login
- POST /api/auth/register - User registration
- GET /api/profile - Protected profile route

## 🔐 Features

- JWT-based authentication
- Password hashing with bcrypt
- PostgreSQL user storage
- Role-based access control
`
  },
  'openai-gpt-wrapper': {
    'src/gpt_api.py': `import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import os

app = FastAPI()
cache = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

openai.api_key = os.getenv('OPENAI_API_KEY')

class ChatRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 150

@app.post("/chat")
async def chat_completion(request: ChatRequest):
    cache_key = f"chat:{request.model}:{request.prompt}"
    
    cached_response = cache.get(cache_key)
    if cached_response:
        return {"reply": cached_response, "cached": True}
    
    try:
        response = openai.ChatCompletion.create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens
        )
        
        reply = response.choices[0].message.content
        cache.setex(cache_key, 3600, reply)
        
        return {"reply": reply, "cached": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
`,
    'requirements.txt': `fastapi==0.104.1
openai==0.28.1
redis==5.0.1
uvicorn==0.24.0
python-dotenv==1.0.0
`,
    'config.py': `import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
`,
    'README.md': `# OpenAI GPT Wrapper API

Production-ready API wrapper for OpenAI with Redis caching and rate limiting.

## 🚀 Quick Start

\`\`\`bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
uvicorn src.gpt_api:app --reload --port 8000
\`\`\`

## 📡 API Endpoints

- POST /chat - Chat completion with caching

## 🔧 Environment Variables

- OPENAI_API_KEY - Your OpenAI API key
- REDIS_HOST - Redis server host
- REDIS_PORT - Redis server port
- CACHE_TTL - Cache time-to-live in seconds
`
  }
};

// Routes

// Search systems
app.get('/api/v1/search', async (req, res) => {
  try {
    const { q } = req.query;
    let query = 'SELECT * FROM systems WHERE is_active = true';
    const params = [];
    
    if (q) {
      query += ` AND (title ILIKE $1 OR description ILIKE $1 OR array_to_string(tech_stack, ',') ILIKE $1)`;
      params.push(`%${q}%`);
    }
    
    query += ' ORDER BY downloads DESC';
    const result = await pool.query(query, params);
    res.json({ systems: result.rows });
  } catch (err) {
    console.error('Search error:', err);
    res.status(500).json({ error: 'Search failed' });
  }
});

// Get single system
app.get('/api/v1/systems/:slug', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM systems WHERE slug = $1 AND is_active = true',
      [req.params.slug]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'System not found' });
    }
    
    res.json({ system: result.rows[0] });
  } catch (err) {
    console.error('Get system error:', err);
    res.status(500).json({ error: 'Failed to fetch system' });
  }
});

// Get system files
app.get('/api/v1/systems/:slug/files', (req, res) => {
  const files = systemFiles[req.params.slug];
  
  if (!files) {
    return res.status(404).json({ error: 'Files not found for this system' });
  }
  
  res.json({ files });
});

// Get reviews
app.get('/api/v1/systems/:slug/reviews', async (req, res) => {
  try {
    const systemResult = await pool.query(
      'SELECT id FROM systems WHERE slug = $1',
      [req.params.slug]
    );
    
    if (systemResult.rows.length === 0) {
      return res.status(404).json({ error: 'System not found' });
    }
    
    const result = await pool.query(
      `SELECT r.id, r.rating, r.comment, r.created_at, u.name as user_name
       FROM reviews r
       JOIN users u ON r.user_id = u.id
       WHERE r.system_id = $1
       ORDER BY r.created_at DESC`,
      [systemResult.rows[0].id]
    );
    
    res.json({ reviews: result.rows });
  } catch (err) {
    console.error('Get reviews error:', err);
    res.status(500).json({ error: 'Failed to fetch reviews' });
  }
});

// Add review
app.post('/api/v1/systems/:slug/reviews',
  body('rating').isInt({ min: 1, max: 5 }).withMessage('Rating must be between 1 and 5'),
  body('comment').trim().isLength({ min: 1 }).withMessage('Comment is required'),
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const systemResult = await pool.query(
        'SELECT id FROM systems WHERE slug = $1',
        [req.params.slug]
      );
      
      if (systemResult.rows.length === 0) {
        return res.status(404).json({ error: 'System not found' });
      }
      
      const systemId = systemResult.rows[0].id;
      const userId = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'; // Demo user
      
      await pool.query(
        'INSERT INTO reviews (system_id, user_id, rating, comment) VALUES ($1, $2, $3, $4)',
        [systemId, userId, req.body.rating, req.body.comment]
      );
      
      // Update average rating
      const avgResult = await pool.query(
        'SELECT AVG(rating)::DECIMAL(2,1) as avg_rating FROM reviews WHERE system_id = $1',
        [systemId]
      );
      
      await pool.query(
        'UPDATE systems SET rating = $1 WHERE id = $2',
        [avgResult.rows[0].avg_rating || 0, systemId]
      );
      
      res.status(201).json({
        message: 'Review added successfully',
        rating: avgResult.rows[0].avg_rating
      });
    } catch (err) {
      console.error('Add review error:', err);
      res.status(500).json({ error: 'Failed to add review' });
    }
  }
);

// Download system
app.get('/api/v1/download/:slug', async (req, res) => {
  const slug = req.params.slug;
  const files = systemFiles[slug];
  
  if (!files) {
    return res.status(404).json({ error: 'System not found' });
  }

  try {
    // Increment download count
    await pool.query(
      'UPDATE systems SET downloads = downloads + 1 WHERE slug = $1',
      [slug]
    );

    // Create zip archive
    const archive = archiver('zip', { zlib: { level: 9 } });
    
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', `attachment; filename="${slug}.zip"`);
    
    archive.on('error', (err) => {
      console.error('Archive error:', err);
      res.status(500).json({ error: 'Failed to create archive' });
    });
    
    archive.pipe(res);
    
    // Add all files to archive
    Object.entries(files).forEach(([filePath, content]) => {
      archive.append(content, { name: filePath });
    });
    
    await archive.finalize();
  } catch (err) {
    console.error('Download error:', err);
    res.status(500).json({ error: 'Download failed' });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NexusAPI running on http://localhost:${PORT}`);
  console.log(`📊 Database user: ${currentUser}`);
});
