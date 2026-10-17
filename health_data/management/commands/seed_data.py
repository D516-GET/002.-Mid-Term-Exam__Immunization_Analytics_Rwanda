import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from coverage.models import ImmunizationRecord, MaternalVisit
from health_data.models import Child, District, HealthFacility, Vaccine

FEMALE_NAMES = ['Keza', 'Ineza', 'Uwase', 'Umutoni', 'Mutesi', 'Isimbi', 'Ingabire',
                'Aline', 'Divine', 'Grace', 'Joyce', 'Claudine', 'Teta', 'Umuhoza']
MALE_NAMES = ['Mugisha', 'Eric', 'Patrick', 'Emmanuel', 'David', 'Nshuti', 'Manzi',
              'Gasana', 'Kwizera', 'Ntwari', 'Muhire', 'Byiringiro', 'Kamanzi', 'Habimana']
SURNAMES = ['Uwimana', 'Habimana', 'Niyonsenga', 'Nkurunziza', 'Hakizimana', 'Mukamana',
            'Bizimana', 'Nsengiyumva', 'Uwizeye', 'Ndayisaba', 'Mugabo', 'Iradukunda',
            'Tuyisenge', 'Nzeyimana', 'Munyaneza', 'Kayitesi', 'Dusabimana']
VISIT_NOTES = ['', '', 'Routine check-up', 'Iron and folic acid given',
               'Counselled on nutrition', 'Referred to district hospital']


class Command(BaseCommand):
    help = 'Generate simulated facilities, children, immunization records and maternal visits'

    def add_arguments(self, parser):
        parser.add_argument('--children', type=int, default=3000, help='Total children to create')
        parser.add_argument('--seed', type=int, default=15, help='Random seed (same seed = same data)')
        parser.add_argument('--reset', action='store_true', help='Delete existing simulated data first')

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(options['seed'])
        today = date.today()

        districts = list(District.objects.all())
        vaccines = list(Vaccine.objects.all())
        if not districts or not vaccines:
            raise CommandError('Run load_districts and load_vaccines first.')
        total_child_pop = sum(d.children_0_17 for d in districts)
        if total_child_pop == 0:
            raise CommandError('Run load_child_counts first.')

        if Child.objects.exists() or HealthFacility.objects.exists():
            if not options['reset']:
                raise CommandError('Simulated data already exists. Use --reset to replace it.')
            ImmunizationRecord.objects.all().delete()
            MaternalVisit.objects.all().delete()
            Child.objects.all().delete()
            HealthFacility.objects.all().delete()

        # 1. Facilities: sized by district population
        facilities_by_district = {}
        for d in districts:
            facilities = [HealthFacility(name=f'{d.name} District Hospital',
                                         facility_type='DH', district=d)]
            for i in range(1, max(3, round(d.population / 50000)) + 1):
                facilities.append(HealthFacility(name=f'{d.name} Health Center {i}',
                                                 facility_type='HC', district=d))
            for i in range(1, d.population // 100000 + 1):
                facilities.append(HealthFacility(name=f'{d.name} Health Post {i}',
                                                 facility_type='HP', district=d))
            HealthFacility.objects.bulk_create(facilities)
            facilities_by_district[d.id] = list(HealthFacility.objects.filter(district=d))

        # 2. Each district gets its own performance level
        district_factor = {d.id: rng.uniform(0.82, 0.99) for d in districts}

        # 3. Children: shared out in proportion to the real 0-17 counts
        children = []
        children_per_district = {}
        for d in districts:
            n = max(1, round(options['children'] * d.children_0_17 / total_child_pop))
            children_per_district[d.id] = n
            for _ in range(n):
                sex = rng.choice(['F', 'M'])
                given = rng.choice(FEMALE_NAMES if sex == 'F' else MALE_NAMES)
                children.append(Child(
                    full_name=f'{given} {rng.choice(SURNAMES)}',
                    date_of_birth=today - timedelta(days=rng.randint(0, 1095)),
                    sex=sex,
                    district=d,
                ))
        Child.objects.bulk_create(children, batch_size=500)

        # 4. Immunization records
        records = []
        for child in Child.objects.all():
            facility = rng.choice(facilities_by_district[child.district_id])
            factor = district_factor[child.district_id]
            for vaccine in vaccines:
                spacing = 180 if 'Measles' in vaccine.name else 30
                for dose in range(1, vaccine.doses_required + 1):
                    if rng.random() > factor * (0.97 ** (dose - 1)):
                        break  # child dropped out of this vaccine series
                    age_days = vaccine.recommended_age_months * 30 + (dose - 1) * spacing
                    given = child.date_of_birth + timedelta(days=age_days + rng.randint(0, 14))
                    if given > today:
                        break  # child is too young for this dose yet
                    records.append(ImmunizationRecord(
                        child=child, vaccine=vaccine, facility=facility,
                        date_given=given, dose_number=dose,
                    ))
        ImmunizationRecord.objects.bulk_create(records, batch_size=1000)

        # 5. Maternal (antenatal) visits
        visits = []
        mother_no = 0
        for d in districts:
            factor = district_factor[d.id]
            n_mothers = max(1, round(children_per_district[d.id] / 3))
            for _ in range(n_mothers):
                mother_no += 1
                code = f'MTH-{mother_no:05d}'
                facility = rng.choice(facilities_by_district[d.id])
                visit_date = today - timedelta(days=rng.randint(0, 540))
                for number in range(1, 5):
                    if number > 1:
                        if rng.random() > factor * 0.9:
                            break  # mother stopped attending
                        visit_date += timedelta(days=rng.randint(30, 60))
                        if visit_date > today:
                            break
                    visits.append(MaternalVisit(
                        facility=facility, mother_code=code, visit_number=number,
                        visit_date=visit_date, notes=rng.choice(VISIT_NOTES),
                    ))
        MaternalVisit.objects.bulk_create(visits, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(
            f'Done: {HealthFacility.objects.count()} facilities, {Child.objects.count()} children, '
            f'{len(records)} immunization records, {len(visits)} maternal visits.'
        ))