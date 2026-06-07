import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from payroll.models import TaxYear, PAYEBracket, TaxRebate, MedicalCredit, TaxThreshold, UIFConfig, SDLConfig, ETIConfig
import re

class Command(BaseCommand):
    help = 'Import SARS tax rules from JSON files'

    def add_arguments(self, parser):
        parser.add_argument('data_dir', type=str, help='Directory containing the tax JSON files')

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.import_year_data(data)

    def import_year_data(self, data):
        tax_year_label = f"{data['tax_year']-1}/{data['tax_year']}"
        self.stdout.write(f"Importing data for {tax_year_label}...")
        
        tax_year, created = TaxYear.objects.get_or_create(
            label=tax_year_label,
            defaults={
                'start_date': data['start_date'],
                'end_date': data['end_date']
            }
        )
        
        if not created:
            # Clear existing data for this tax year to allow re-imports
            PAYEBracket.objects.filter(tax_year=tax_year).delete()
            TaxRebate.objects.filter(tax_year=tax_year).delete()
            TaxThreshold.objects.filter(tax_year=tax_year).delete()
            UIFConfig.objects.filter(tax_year=tax_year).delete()
            SDLConfig.objects.filter(tax_year=tax_year).delete()
            ETIConfig.objects.filter(tax_year=tax_year).delete()
            if hasattr(tax_year, 'medical_credit'):
                tax_year.medical_credit.delete()

        # Import PAYE Brackets
        for bracket in data['income_tax_brackets']:
            PAYEBracket.objects.create(
                tax_year=tax_year,
                from_amount=Decimal(str(bracket['threshold'])),
                base_tax=Decimal(str(bracket['base_amount'])),
                rate=Decimal(str(bracket['rate']))
            )

        # Import Tax Rebates
        rebates = data['tax_rebates']
        TaxRebate.objects.create(tax_year=tax_year, type='primary', amount=Decimal(str(rebates['primary'])))
        TaxRebate.objects.create(tax_year=tax_year, type='secondary', amount=Decimal(str(rebates['secondary'])))
        TaxRebate.objects.create(tax_year=tax_year, type='tertiary', amount=Decimal(str(rebates['tertiary'])))

        # Import Tax Thresholds
        thresholds = data['tax_thresholds']
        TaxThreshold.objects.create(
            tax_year=tax_year,
            age_under_65=Decimal(str(thresholds['under_65'])),
            age_65_to_75=Decimal(str(thresholds['age_65_to_74'])),
            age_75_over=Decimal(str(thresholds['age_75_plus']))
        )

        # Import Medical Credits
        medical = data['medical_scheme_credits']
        MedicalCredit.objects.create(
            tax_year=tax_year,
            first_dependent=Decimal(str(medical['main_member'])),
            second_dependent=Decimal(str(medical['first_dependent'])),
            additional_dependents=Decimal(str(medical['additional_dependent']))
        )

        # Import UIF Config
        uif = data['uif']
        rate = Decimal(str(uif['employee_rate']))
        
        # Handle mid-year cap changes (like in 2021/2022)
        if 'monthly_cap' in uif:
            monthly_remuneration_cap = Decimal(str(uif['monthly_cap']))
        elif 'monthly_cap_from_june' in uif:
            # For 2022, we take the latest cap for the whole year for simplicity in this model
            monthly_remuneration_cap = Decimal(str(uif['monthly_cap_from_june']))
        else:
            monthly_remuneration_cap = Decimal('0.00')

        cap = monthly_remuneration_cap * rate
        UIFConfig.objects.create(
            tax_year=tax_year,
            rate=rate,
            employee_cap=cap,
            employer_cap=cap
        )

        # Import SDL Config
        sdl = data.get('sdl')
        if sdl:
            SDLConfig.objects.create(
                tax_year=tax_year,
                rate=Decimal(str(sdl['rate'])),
                annual_threshold=Decimal(str(sdl['annual_threshold']))
            )

        # Import ETI Config
        eti = data.get('eti')
        if eti:
            for phase_name in ['phase_1', 'phase_2']:
                phase_num = 1 if phase_name == 'phase_1' else 2
                brackets = eti[phase_name]['remuneration_brackets']
                for b in brackets:
                    range_min = Decimal(str(b['min']))
                    range_max = Decimal(str(b['max']))
                    fixed_amount = Decimal('0.00')
                    percentage = Decimal('0.0000')
                    excess_percentage = Decimal('0.0000')
                    excess_threshold = Decimal('0.00')

                    if 'fixed_amount' in b:
                        fixed_amount = Decimal(str(b['fixed_amount']))
                    
                    formula = b.get('formula', '')
                    if formula:
                        # Case 1: "0.5 * remuneration"
                        match1 = re.match(r'([\d\.]+) \* remuneration', formula)
                        if match1:
                            percentage = Decimal(match1.group(1))
                        
                        # Case 2: "1000 - (0.5 * (remuneration - 4500))"
                        match2 = re.match(r'([\d\.]+) - \(([\d\.]+) \* \(remuneration - ([\d\.]+)\)\)', formula)
                        if match2:
                            fixed_amount = Decimal(match2.group(1))
                            excess_percentage = Decimal(match2.group(2))
                            excess_threshold = Decimal(match2.group(3))

                    ETIConfig.objects.create(
                        tax_year=tax_year,
                        phase=phase_num,
                        range_min=range_min,
                        range_max=range_max,
                        fixed_amount=fixed_amount,
                        percentage=percentage,
                        excess_percentage=excess_percentage,
                        excess_threshold=excess_threshold
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully imported data for {tax_year_label}"))
