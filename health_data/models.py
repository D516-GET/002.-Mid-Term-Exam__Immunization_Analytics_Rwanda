from django.db import models


class District(models.Model):
    PROVINCE_CHOICES = [
        ('Kigali City', 'Kigali City'),
        ('Southern', 'Southern'),
        ('Western', 'Western'),
        ('Northern', 'Northern'),
        ('Eastern', 'Eastern'),
    ]

    name = models.CharField(max_length=100, unique=True)
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES)
    population = models.PositiveIntegerField(default=0)
    children_0_17 = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HealthFacility(models.Model):
    FACILITY_TYPES = [
        ('HP', 'Health Post'),
        ('HC', 'Health Center'),
        ('DH', 'District Hospital'),
        ('RH', 'Referral Hospital'),
    ]

    name = models.CharField(max_length=150)
    facility_type = models.CharField(max_length=2, choices=FACILITY_TYPES, default='HC')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='facilities')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'health facilities'

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class Vaccine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    recommended_age_months = models.PositiveSmallIntegerField(default=0)
    doses_required = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Child(models.Model):
    SEX_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
    ]

    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='children')

    class Meta:
        ordering = ['full_name']
        verbose_name_plural = 'children'

    def __str__(self):
        return self.full_name