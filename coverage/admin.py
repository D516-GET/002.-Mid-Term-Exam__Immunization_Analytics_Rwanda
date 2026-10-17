from django.contrib import admin

from .models import ImmunizationRecord, MaternalVisit, NationalCoverage


@admin.register(ImmunizationRecord)
class ImmunizationRecordAdmin(admin.ModelAdmin):
    list_display = ('child', 'vaccine', 'facility', 'dose_number', 'date_given')
    list_filter = ('vaccine', 'facility__district')
    search_fields = ('child__full_name',)
    date_hierarchy = 'date_given'
    autocomplete_fields = ['child']


@admin.register(MaternalVisit)
class MaternalVisitAdmin(admin.ModelAdmin):
    list_display = ('mother_code', 'visit_number', 'facility', 'visit_date')
    list_filter = ('visit_number', 'facility__district')
    search_fields = ('mother_code',)


@admin.register(NationalCoverage)
class NationalCoverageAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'vaccine', 'year', 'coverage_percent')
    list_filter = ('indicator', 'year')