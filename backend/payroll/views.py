from django.db.models import Sum, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
import os
from .utils import generate_payslip_pdf
from .models import (
    Organization, Employee, TaxYear, PAYEBracket, TaxRebate,
    MedicalCredit, TaxThreshold, UIFConfig, PayrollRun, Payslip, PayslipItem,
    SDLConfig, ETIConfig
)
from .serializers import (
    OrganizationSerializer, EmployeeSerializer, TaxYearSerializer,
    PAYEBracketSerializer, TaxRebateSerializer, MedicalCreditSerializer,
    TaxThresholdSerializer, UIFConfigSerializer, PayrollRunSerializer,
    PayslipSerializer, PayslipItemSerializer, SDLConfigSerializer,
    ETIConfigSerializer
)

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        org = self.get_object()
        employee_count = Employee.objects.filter(organization=org, status='active').count()
        
        # Monthly totals (current month)
        from django.utils import timezone
        now = timezone.now()
        
        latest_runs = PayrollRun.objects.filter(
            organization=org, 
            period_month=now.month, 
            period_year=now.year,
            status='finalized'
        )
        
        total_paye = Payslip.objects.filter(payroll_run__in=latest_runs).aggregate(Sum('paye'))['paye__sum'] or 0
        total_net = Payslip.objects.filter(payroll_run__in=latest_runs).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
        
        # Recent runs
        recent_runs = PayrollRun.objects.filter(organization=org).order_by('-period_year', '-period_month')[:5]
        recent_runs_data = [
            {
                'id': run.id,
                'period': f"{run.period_month}/{run.period_year}",
                'status': run.status,
                'employee_count': Payslip.objects.filter(payroll_run=run).count()
            } for run in recent_runs
        ]

        return Response({
            'employee_count': employee_count,
            'total_paye_mtd': total_paye,
            'total_net_mtd': total_net,
            'recent_runs': recent_runs_data
        })

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

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer

    def get_queryset(self):
        queryset = PayrollRun.objects.all()
        organization_id = self.request.query_params.get('organization_id')
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

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
        try:
            file_path = generate_payslip_pdf(payslip)
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            else:
                return Response({"error": "PDF file not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PayslipItemViewSet(viewsets.ModelViewSet):
    queryset = PayslipItem.objects.all()
    serializer_class = PayslipItemSerializer

class SDLConfigViewSet(viewsets.ModelViewSet):
    queryset = SDLConfig.objects.all()
    serializer_class = SDLConfigSerializer

class ETIConfigViewSet(viewsets.ModelViewSet):
    queryset = ETIConfig.objects.all()
    serializer_class = ETIConfigSerializer
