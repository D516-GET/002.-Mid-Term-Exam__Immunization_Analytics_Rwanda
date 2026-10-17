import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from health_data.models import District


class Command(BaseCommand):
    help = 'Load districts from data/districts.csv into the database'

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / 'data' / 'districts.csv'
        if not csv_path.exists():
            raise CommandError(f'File not found: {csv_path}')

        created_count = 0
        updated_count = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
            for row in csv.DictReader(csv_file):
                name = row['name'].strip()
                population_text = row['population'].strip().replace(',', '')
                population = int(population_text) if population_text else 0

                if population == 0:
                    self.stdout.write(self.style.WARNING(f'No population for {name}'))

                district, created = District.objects.update_or_create(
                    name=name,
                    defaults={
                        'province': row['province'].strip(),
                        'population': population,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done: {created_count} created, {updated_count} updated.'
        ))