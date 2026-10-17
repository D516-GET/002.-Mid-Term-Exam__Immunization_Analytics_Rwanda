from django.contrib import admin

from .models import Child, District, HealthFacility, Vaccine


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'population', 'children_0_17')
    list_filter = ('province',)
    search_fields = ('name',)


@admin.register(HealthFacility)
class HealthFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'facility_type', 'district')
    list_filter = ('facility_type', 'district')
    search_fields = ('name',)


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ('name', 'recommended_age_months', 'doses_required')


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'sex', 'date_of_birth', 'district')
    list_filter = ('sex', 'district')
    search_fields = ('full_name',)
    date_hierarchy = 'date_of_birth'