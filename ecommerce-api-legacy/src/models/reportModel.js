const db = require('../database');

class ReportModel {
  // Substitui o loop curso -> matrícula -> usuário/pagamento (finding
  // MEDIUM "N+1 Query Problem") por uma única query agregada com JOIN.
  static async financialSummaryRows() {
    return db.all(`
      SELECT
        c.id AS course_id,
        c.title AS course_title,
        e.id AS enrollment_id,
        u.name AS student_name,
        p.amount AS amount,
        p.status AS status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u ON u.id = e.user_id
      LEFT JOIN payments p ON p.enrollment_id = e.id
      ORDER BY c.id
    `);
  }
}

module.exports = ReportModel;
