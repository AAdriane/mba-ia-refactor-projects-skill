const FinancialReportService = require('../services/financialReportService');

class AdminController {
  static async financialReport(req, res) {
    const report = await FinancialReportService.generate();
    res.json(report);
  }
}

module.exports = AdminController;
