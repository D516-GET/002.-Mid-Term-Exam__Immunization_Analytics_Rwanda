from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from health_data.models import Child, HealthFacility, Vaccine


class ImmunizationRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='immunizations')
    vaccine = models.ForeignKey(Vaccine, on_delete=models.PROTECT, related_name='records')
    facility = models.ForeignKey(HealthFacility, on_delete=models.PROTECT, related_name='immunizations')
    date_given = models.DateField()
    dose_number = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['-date_given']
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'vaccine', 'dose_number'],
                name='unique_child_vaccine_dose',
            )
        ]

    def __str__(self):
        return f"{self.child} - {self.vaccine} (dose {self.dose_number})"

    def clean(self):
        if self.date_given and self.date_given > date.today():
            raise ValidationError({'date_given': 'The date given cannot be in the future.'})
        if self.child_id and self.date_given and self.date_given < self.child.date_of_birth:
            raise ValidationError({'date_given': 'The vaccine cannot be given before the child was born.'})
        if self.vaccine_id and self.dose_number > self.vaccine.doses_required:
            raise ValidationError({
                'dose_number': f'{self.vaccine.name} requires only {self.vaccine.doses_required} dose(s).'
            })


class MaternalVisit(models.Model):
    facility = models.ForeignKey(HealthFacility, on_delete=models.PROTECT, related_name='maternal_visits')
    mother_code = models.CharField(max_length=20)
    visit_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text='Antenatal care visit number (ANC1 to ANC4)',
    )
    visit_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-visit_date']
        constraints = [
            models.UniqueConstraint(
                fields=['mother_code', 'visit_number'],
                name='unique_mother_visit_number',
            )
        ]

    def __str__(self):
        return f"{self.mother_code} - ANC{self.visit_number}"

    def clean(self):
        if self.visit_date and self.visit_date > date.today():
            raise ValidationError({'visit_date': 'The visit date cannot be in the future.'})


class NationalCoverage(models.Model):
    """Real WHO-UNICEF (WUENIC) national coverage estimate for Rwanda."""
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE, related_name='national_coverage')
    indicator = models.CharField(max_length=10, help_text='WUENIC indicator code, e.g. DTP3, MCV1')
    year = models.PositiveSmallIntegerField()
    coverage_percent = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])

    class Meta:
        ordering = ['indicator', 'year']
        verbose_name_plural = 'national coverage'
        constraints = [
            models.UniqueConstraint(fields=['indicator', 'year'], name='unique_indicator_year')
        ]

    def __str__(self):
        return f"{self.indicator} {self.year}: {self.coverage_percent}%"