import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from health_data.models import Vaccine


class Command(BaseCommand):
    help = 'Load vaccines from data/vaccines.csv into the database'

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / 'data' / 'vaccines.csv'
        if not csv_path.exists():
            raise CommandError(f'File not found: {csv_path}')

        created_count = 0
        updated_count = 0

        with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
            for row in csv.DictReader(csv_file):
                vaccine, created = Vaccine.objects.update_or_create(
                    name=row['name'].strip(),
                    defaults={
                        'recommended_age_months': int(row['recommended_age_months']),
                        'doses_required': int(row['doses_required']),
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done: {created_count} created, {updated_count} updated.'
        ))