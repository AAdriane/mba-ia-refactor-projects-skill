const sqlite3 = require('sqlite3').verbose();

const config = require('./config');

const db = new sqlite3.Database(config.dbFile);

// Wrapper Promise sobre a API do driver sqlite3, que é exclusivamente
// baseada em callbacks. Base técnica para eliminar o "pyramid of callbacks"
// do AppManager.js original (ver refactoring-playbook.md #13).
function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function callback(err) {
      if (err) return reject(err);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) return reject(err);
      resolve(row);
    });
  });
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function initSchema() {
  await run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
  await run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
  await run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
  await run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
  await run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seed() {
  const existingUser = await get('SELECT id FROM users WHERE email = ?', ['leonan@fullcycle.com.br']);
  if (existingUser) return;

  // Requerido de forma tardia para evitar dependência circular no boot
  // (passwordService não depende de database.js).
  const { hashPassword } = require('./services/passwordService');

  const userResult = await run(
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')],
  );

  await run(
    'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
    ['Clean Architecture', 997.0, 'Docker', 497.0],
  );

  const enrollmentResult = await run(
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userResult.lastID, 1],
  );

  await run(
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentResult.lastID, 997.0, 'PAID'],
  );
}

module.exports = { db, run, get, all, initSchema, seed };
