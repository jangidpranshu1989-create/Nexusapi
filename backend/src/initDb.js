const { Pool } = require('pg');
const os = require('os');

const currentUser = os.userInfo().username;

const pool = new Pool({
  host: 'localhost',
  database: 'nexusapi',
  user: currentUser,
  password: 'postgres',
  port: 5432,
});

const createTables = async () => {
  const client = await pool.connect();
  try {
    console.log('🔄 Creating database tables...');
    
    await client.query('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"');

    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(50) DEFAULT 'developer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        icon VARCHAR(50) DEFAULT '📦'
      )
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS systems (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        title VARCHAR(255) NOT NULL,
        slug VARCHAR(255) UNIQUE NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT,
        tech_stack TEXT[],
        setup_time VARCHAR(50) DEFAULT '5 mins',
        downloads INT DEFAULT 0,
        rating DECIMAL(2,1) DEFAULT 0.0,
        is_active BOOLEAN DEFAULT true
      )
    `);

    await client.query(`
      CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        system_id UUID REFERENCES systems(id) ON DELETE CASCADE,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        rating INT CHECK (rating BETWEEN 1 AND 5),
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('✅ All tables created successfully');
  } catch (err) {
    console.error('❌ Error creating tables:', err.message);
    throw err;
  } finally {
    client.release();
    await pool.end();
  }
};

createTables()
  .then(() => process.exit(0))
  .catch(() => process.exit(1));
