from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from health_data.models import Child, District, HealthFacility, Vaccine

from .forms import ImmunizationRecordForm
from .models import ImmunizationRecord, MaternalVisit, NationalCoverage

COVERAGE_TARGET = 90  # percent


def dashboard(request):
    total_children = Child.objects.count()
    bcg_given = ImmunizationRecord.objects.filter(
        vaccine__name='BCG', dose_number=1
    ).count()
    overall_rate = round(100 * bcg_given / total_children, 1) if total_children else 0

    districts = District.objects.annotate(
        child_total=Count('children', distinct=True),
        bcg_total=Count(
            'children__immunizations',
            filter=Q(
                children__immunizations__vaccine__name='BCG',
                children__immunizations__dose_number=1,
            ),
        ),
    )

    district_rows = []
    for d in districts:
        rate = round(100 * d.bcg_total / d.child_total, 1) if d.child_total else 0
        district_rows.append({
            'name': d.name,
            'province': d.province,
            'children': d.child_total,
            'rate': rate,
            'below_target': rate < COVERAGE_TARGET,
        })
    district_rows.sort(key=lambda row: row['rate'])
    below_target = sum(1 for row in district_rows if row['below_target'])

    national_bcg = NationalCoverage.objects.filter(indicator='BCG').order_by('-year').first()
    recent_records = ImmunizationRecord.objects.select_related(
        'child', 'vaccine', 'facility'
    )[:10]

    context = {
        'total_children': total_children,
        'total_records': ImmunizationRecord.objects.count(),
        'total_facilities': HealthFacility.objects.count(),
        'total_visits': MaternalVisit.objects.count(),
        'overall_rate': overall_rate,
        'below_target': below_target,
        'target': COVERAGE_TARGET,
        'national_bcg': national_bcg,
        'district_rows': district_rows,
        'recent_records': recent_records,
    }
    return render(request, 'coverage/dashboard.html', context)


def record_list(request):
    query = request.GET.get('q', '').strip()
    vaccine_id = request.GET.get('vaccine', '')
    records = ImmunizationRecord.objects.select_related('child', 'vaccine', 'facility')
    if query:
        records = records.filter(child__full_name__icontains=query)
    if vaccine_id.isdigit():
        records = records.filter(vaccine_id=int(vaccine_id))
    page = Paginator(records, 25).get_page(request.GET.get('page'))
    context = {
        'page': page,
        'query': query,
        'vaccine_id': vaccine_id,
        'vaccines': Vaccine.objects.all(),
    }
    return render(request, 'coverage/record_list.html', context)


@login_required
def record_create(request):
    initial = {}
    if request.GET.get('child', '').isdigit():
        initial['child'] = int(request.GET['child'])
    form = ImmunizationRecordForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        record = form.save()
        messages.success(request, f'{record.vaccine.name} (dose {record.dose_number}) was recorded.')
        return redirect('health_data:child_detail', pk=record.child_id)
    return render(request, 'coverage/record_form.html', {'form': form, 'title': 'Record an immunization'})


@login_required
def record_update(request, pk):
    record = get_object_or_404(ImmunizationRecord, pk=pk)
    form = ImmunizationRecordForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'The immunization record was updated.')
        return redirect('health_data:child_detail', pk=record.child_id)
    return render(request, 'coverage/record_form.html', {'form': form, 'title': 'Edit immunization record'})


@login_required
def record_delete(request, pk):
    record = get_object_or_404(
        ImmunizationRecord.objects.select_related('child', 'vaccine'), pk=pk
    )
    if request.method == 'POST':
        child_pk = record.child_id
        record.delete()
        messages.success(request, 'The immunization record was deleted.')
        return redirect('health_data:child_detail', pk=child_pk)
    return render(request, 'coverage/record_confirm_delete.html', {'record': record})
def visit_list(request):
    query = request.GET.get('q', '').strip()
    visit_number = request.GET.get('visit', '')
    visits = MaternalVisit.objects.select_related('facility', 'facility__district')
    if query:
        visits = visits.filter(mother_code__icontains=query)
    if visit_number.isdigit():
        visits = visits.filter(visit_number=int(visit_number))
    page = Paginator(visits, 25).get_page(request.GET.get('page'))
    context = {'page': page, 'query': query, 'visit_number': visit_number}
    return render(request, 'coverage/visit_list.html', context)