import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from coverage.models import NationalCoverage
from health_data.models import Vaccine


class Command(BaseCommand):
    help = 'Load WHO-UNICEF national coverage estimates from data/national_coverage.csv'

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / 'data' / 'national_coverage.csv'
        if not csv_path.exists():
            raise CommandError(f'File not found: {csv_path}')

        created_count = 0
        updated_count = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
            for row in csv.DictReader(csv_file):
                vaccine_name = row['vaccine'].strip()
                try:
                    vaccine = Vaccine.objects.get(name=vaccine_name)
                except Vaccine.DoesNotExist:
                    raise CommandError(
                        f'Vaccine not found: {vaccine_name}. Run load_vaccines first.'
                    )

                obj, created = NationalCoverage.objects.update_or_create(
                    indicator=row['indicator'].strip(),
                    year=int(row['year']),
                    defaults={
                        'vaccine': vaccine,
                        'coverage_percent': int(row['coverage_percent']),
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done: {created_count} created, {updated_count} updated.'
        ))