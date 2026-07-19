const { Pool } = require('pg');
const { v4: uuidv4 } = require('uuid');
const os = require('os');

const currentUser = os.userInfo().username;

const pool = new Pool({
  host: 'localhost',
  database: 'nexusapi',
  user: currentUser,
  password: 'postgres',
  port: 5432,
});

const seed = async () => {
  const client = await pool.connect();
  try {
    console.log('🌱 Seeding database...');

    const userId = uuidv4();
    const system1Id = uuidv4();
    const system2Id = uuidv4();
    const system3Id = uuidv4();

    // Insert demo user
    await client.query(
      'INSERT INTO users (id, email, password_hash, name, role) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (email) DO NOTHING',
      [userId, 'demo@nexusapi.dev', 'hashed_demo', 'Demo Developer', 'developer']
    );

    // Insert categories
    await client.query(
      'INSERT INTO categories (name, slug, icon) VALUES ($1, $2, $3) ON CONFLICT (slug) DO NOTHING',
      ['File Converters', 'file-converters', '🔄']
    );
    await client.query(
      'INSERT INTO categories (name, slug, icon) VALUES ($1, $2, $3) ON CONFLICT (slug) DO NOTHING',
      ['Authentication', 'auth', '🔐']
    );
    await client.query(
      'INSERT INTO categories (name, slug, icon) VALUES ($1, $2, $3) ON CONFLICT (slug) DO NOTHING',
      ['AI & ML', 'ai-ml', '🤖']
    );

    // Insert systems
    await client.query(
      'INSERT INTO systems (id, title, slug, category, description, tech_stack, setup_time, downloads, rating) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
      [system1Id, 'Universal File Converter', 'universal-file-converter', 'file-converters',
       'Convert between 50+ file formats instantly using FFmpeg and Python.',
       ['Python', 'FastAPI', 'FFmpeg'], '3 mins', 245, 4.5]
    );

    await client.query(
      'INSERT INTO systems (id, title, slug, category, description, tech_stack, setup_time, downloads, rating) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
      [system2Id, 'JWT Authentication System', 'jwt-authentication-system', 'auth',
       'Plug-and-play JWT auth with refresh tokens, roles and PostgreSQL.',
       ['Node.js', 'Express', 'JWT', 'PostgreSQL'], '2 mins', 189, 4.2]
    );

    await client.query(
      'INSERT INTO systems (id, title, slug, category, description, tech_stack, setup_time, downloads, rating) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
      [system3Id, 'OpenAI GPT Wrapper', 'openai-gpt-wrapper', 'ai-ml',
       'Production-ready API wrapper for OpenAI with rate limiting and Redis cache.',
       ['Python', 'FastAPI', 'Redis', 'OpenAI'], '4 mins', 156, 4.8]
    );

    // Insert reviews
    await client.query(
      'INSERT INTO reviews (system_id, user_id, rating, comment) VALUES ($1, $2, $3, $4)',
      [system1Id, userId, 5, 'Works like a charm! Saved me hours of work.']
    );
    await client.query(
      'INSERT INTO reviews (system_id, user_id, rating, comment) VALUES ($1, $2, $3, $4)',
      [system2Id, userId, 4, 'Solid auth boilerplate, well documented.']
    );
    await client.query(
      'INSERT INTO reviews (system_id, user_id, rating, comment) VALUES ($1, $2, $3, $4)',
      [system1Id, userId, 4, 'Great file converter, needs more format support.']
    );

    console.log('✅ Seed data inserted successfully');
  } catch (err) {
    console.error('❌ Error seeding database:', err.message);
    throw err;
  } finally {
    client.release();
    await pool.end();
  }
};

seed()
  .then(() => process.exit(0))
  .catch(() => process.exit(1));
