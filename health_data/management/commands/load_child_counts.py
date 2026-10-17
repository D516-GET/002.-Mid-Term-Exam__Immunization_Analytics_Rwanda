from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from health_data.models import District


class Command(BaseCommand):
    help = 'Load children (0-17) counts per district from NISR Table 38'

    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR) / 'data' / 'PHC5-2022_Main_Indicators.xlsx'
        if not path.exists():
            raise CommandError(f'File not found: {path}')

        df = pd.read_excel(path, sheet_name='Table 38', header=None)

        updated = set()
        for _, row in df.iterrows():
            name = row[1]
            if not isinstance(name, str):
                continue
            district = District.objects.filter(name=name.strip()).first()
            if district is None:
                continue  # skips Rwanda, CoK, province rows and header rows
            district.children_0_17 = int(row[2])
            district.save(update_fields=['children_0_17'])
            updated.add(district.name)

        all_names = set(District.objects.values_list('name', flat=True))
        missing = all_names - updated
        if missing:
            self.stdout.write(self.style.WARNING(f'Not found in Excel: {sorted(missing)}'))
        self.stdout.write(self.style.SUCCESS(f'Done: {len(updated)} districts updated.'))