from flask import jsonify

from services.report_service import ReportService

report_service = ReportService()


class ReportController:
    @staticmethod
    def summary():
        return jsonify(report_service.summary()), 200

    @staticmethod
    def user_report(user_id):
        return jsonify(report_service.user_report(user_id)), 200
