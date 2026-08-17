const db = require('../database');

class AuditLogModel {
  static async record(action) {
    return db.run(
      "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
      [action],
    );
  }
}

module.exports = AuditLogModel;
