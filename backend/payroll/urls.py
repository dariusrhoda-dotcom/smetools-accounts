from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, EmployeeViewSet, TaxYearViewSet,
    PAYEBracketViewSet, TaxRebateViewSet, MedicalCreditViewSet,
    TaxThresholdViewSet, UIFConfigViewSet, SDLConfigViewSet, PayrollRunViewSet,
    PayslipViewSet, PayslipItemViewSet
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'tax-years', TaxYearViewSet)
router.register(r'paye-brackets', PAYEBracketViewSet)
router.register(r'tax-rebates', TaxRebateViewSet)
router.register(r'medical-credits', MedicalCreditViewSet)
router.register(r'tax-thresholds', TaxThresholdViewSet)
router.register(r'uif-configs', UIFConfigViewSet)
router.register(r'sdl-configs', SDLConfigViewSet)
router.register(r'payroll-runs', PayrollRunViewSet)
router.register(r'payslips', PayslipViewSet)
router.register(r'payslip-items', PayslipItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
