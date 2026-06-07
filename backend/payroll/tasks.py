import os
from celery import shared_task
from django.core.management import call_command
from .models import TaxYear

@shared_task
def check_for_sars_updates():
    """
    Placeholder for monthly SARS update task.
    Checks /home/team/shared/tax_data/ for any tax years not yet in the DB.
    """
    data_dir = '/home/team/shared/tax_data/'
    if not os.path.exists(data_dir):
        return "Shared tax data directory not found."
    
    found_new = False
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            year_val = filename.split('.')[0]
            # Map "2021" to "2020/2021"
            try:
                year_int = int(year_val)
                label = f"{year_int-1}/{year_int}"
                if not TaxYear.objects.filter(label=label).exists():
                    found_new = True
                    break
            except ValueError:
                continue
    
    if found_new:
        call_command('import_tax_data', data_dir)
        return f"Imported new tax data from {data_dir}"
    
    return "No new tax data found."
