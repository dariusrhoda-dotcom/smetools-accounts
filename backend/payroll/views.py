from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from .models import (
    Organization, Employee, TaxYear, PAYEBracket, TaxRebate,
    MedicalCredit, TaxThreshold, UIFConfig, SDLConfig, PayrollRun, Payslip, PayslipItem
)
from .serializers import (
    OrganizationSerializer, EmployeeSerializer, TaxYearSerializer,
    PAYEBracketSerializer, TaxRebateSerializer, MedicalCreditSerializer,
    TaxThresholdSerializer, UIFConfigSerializer, SDLConfigSerializer, PayrollRunSerializer,
    PayslipSerializer, PayslipItemSerializer
)
from .utils import generate_payslip_pdf
import os

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()
        organization_id = self.request.query_params.get('organization_id')
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

class TaxYearViewSet(viewsets.ModelViewSet):
    queryset = TaxYear.objects.all()
    serializer_class = TaxYearSerializer

class PAYEBracketViewSet(viewsets.ModelViewSet):
    queryset = PAYEBracket.objects.all()
    serializer_class = PAYEBracketSerializer

class TaxRebateViewSet(viewsets.ModelViewSet):
    queryset = TaxRebate.objects.all()
    serializer_class = TaxRebateSerializer

class MedicalCreditViewSet(viewsets.ModelViewSet):
    queryset = MedicalCredit.objects.all()
    serializer_class = MedicalCreditSerializer

class TaxThresholdViewSet(viewsets.ModelViewSet):
    queryset = TaxThreshold.objects.all()
    serializer_class = TaxThresholdSerializer

class UIFConfigViewSet(viewsets.ModelViewSet):
    queryset = UIFConfig.objects.all()
    serializer_class = UIFConfigSerializer

class SDLConfigViewSet(viewsets.ModelViewSet):
    queryset = SDLConfig.objects.all()
    serializer_class = SDLConfigSerializer

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer

    def get_queryset(self):
        queryset = PayrollRun.objects.all()
        organization_id = self.request.query_params.get('organization_id')
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'finalized':
            # Increment ETI months for employees in this run
            payslips = instance.payslips.all()
            for payslip in payslips:
                if payslip.eti > 0:
                    employee = payslip.employee
                    employee.eti_months_claimed += 1
                    employee.save()

class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer

    def get_queryset(self):
        queryset = Payslip.objects.all()
        payroll_run_id = self.request.query_params.get('payroll_run_id')
        if payroll_run_id is not None:
            queryset = queryset.filter(payroll_run_id=payroll_run_id)
        return queryset

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        payslip = self.get_object()
        pdf_path = generate_payslip_pdf(payslip)
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="payslip_{payslip.employee.employee_code}_{payslip.payroll_run.period_year}_{payslip.payroll_run.period_month}.pdf"'
                return response
        else:
            return Response({"error": "Failed to generate PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PayslipItemViewSet(viewsets.ModelViewSet):
    queryset = PayslipItem.objects.all()
    serializer_class = PayslipItemSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "name": "SMETools Payroll API",
        "version": "1.0.0",
        "documentation": request.build_absolute_uri('/api/docs/'),
        "endpoints": {
            "organizations": request.build_absolute_uri('/api/organizations/'),
            "employees": request.build_absolute_uri('/api/employees/'),
            "payroll-runs": request.build_absolute_uri('/api/payroll-runs/'),
            "payslips": request.build_absolute_uri('/api/payslips/'),
        }
    })
