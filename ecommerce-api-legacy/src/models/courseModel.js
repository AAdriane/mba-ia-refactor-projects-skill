const db = require('../database');

class CourseModel {
  static async findActiveById(id) {
    return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
  }

  static async findAll() {
    return db.all('SELECT * FROM courses', []);
  }
}

module.exports = CourseModel;
