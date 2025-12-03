from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rbac.permissions import RbacPermission

class ReportListView(APIView):
    """
    Mock View для получения списка финансовых отчетов.
    Требует права на чтение ресурса 'financial_reports'.
    """
    permission_classes = (IsAuthenticated, RbacPermission)
    resource_name = 'financial_reports'

    def get(self, request):
        mock_data = [
            {"id": 1, "title": "Annual Report 2024", "status": "Finalized"},
            {"id": 2, "title": "Q1 2025 Financials", "status": "Draft"},
            {"id": 3, "title": "Payroll Summary March", "status": "Approved"},
        ]
        return Response(mock_data)