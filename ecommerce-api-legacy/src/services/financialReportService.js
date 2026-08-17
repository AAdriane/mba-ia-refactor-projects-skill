const { PAYMENT_STATUS } = require('../constants');
const ReportModel = require('../models/reportModel');

class FinancialReportService {
  static async generate() {
    const rows = await ReportModel.financialSummaryRows();
    const byCourse = new Map();

    for (const row of rows) {
      if (!byCourse.has(row.course_id)) {
        byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
      }
      const courseData = byCourse.get(row.course_id);

      if (row.enrollment_id) {
        courseData.students.push({
          student: row.student_name || 'Unknown',
          paid: row.amount != null ? row.amount : 0,
        });
        if (row.status === PAYMENT_STATUS.PAID) {
          courseData.revenue += row.amount;
        }
      }
    }

    return Array.from(byCourse.values());
  }
}

module.exports = FinancialReportService;
