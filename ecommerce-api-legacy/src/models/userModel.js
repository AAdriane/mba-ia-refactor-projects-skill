const db = require('../database');
const { hashPassword } = require('../services/passwordService');
const { ValidationError } = require('../errors');

class UserModel {
  static async findByEmail(email) {
    return db.get('SELECT * FROM users WHERE email = ?', [email]);
  }

  static async findById(id) {
    return db.get('SELECT * FROM users WHERE id = ?', [id]);
  }

  static async create({ name, email, password }) {
    if (!password) {
      throw new ValidationError('Senha é obrigatória para criar um novo usuário');
    }
    const passwordHash = hashPassword(password);
    const result = await db.run(
      'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
      [name, email, passwordHash],
    );
    return result.lastID;
  }

  static async deleteCascade(userId) {
    const enrollments = await db.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
    for (const enrollment of enrollments) {
      await db.run('DELETE FROM payments WHERE enrollment_id = ?', [enrollment.id]);
    }
    await db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    await db.run('DELETE FROM users WHERE id = ?', [userId]);
  }
}

module.exports = UserModel;
