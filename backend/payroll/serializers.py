from rest_framework import serializers
from .models import (
    Organization, Employee, TaxYear, PAYEBracket, TaxRebate,
    MedicalCredit, TaxThreshold, UIFConfig, SDLConfig, ETIConfig, PayrollRun, Payslip, PayslipItem
)

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class TaxYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxYear
        fields = '__all__'

class PAYEBracketSerializer(serializers.ModelSerializer):
    class Meta:
        model = PAYEBracket
        fields = '__all__'

class TaxRebateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRebate
        fields = '__all__'

class MedicalCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCredit
        fields = '__all__'

class TaxThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxThreshold
        fields = '__all__'

class UIFConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIFConfig
        fields = '__all__'

class SDLConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDLConfig
        fields = '__all__'

class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = '__all__'

class PayslipItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipItem
        fields = '__all__'

class PayslipSerializer(serializers.ModelSerializer):
    items = PayslipItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payslip
        fields = '__all__'

class ETIConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETIConfig
        fields = '__all__'
