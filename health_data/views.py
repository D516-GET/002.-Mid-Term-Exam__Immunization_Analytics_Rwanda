from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from coverage.models import ImmunizationRecord

from .forms import ChildForm
from .models import Child, District, HealthFacility, Vaccine

COVERAGE_TARGET = 90  # percent


def child_list(request):
    query = request.GET.get('q', '').strip()
    children = Child.objects.select_related('district')
    if query:
        children = children.filter(
            Q(full_name__icontains=query) | Q(district__name__icontains=query)
        )
    page = Paginator(children, 25).get_page(request.GET.get('page'))
    return render(request, 'health_data/child_list.html', {'page': page, 'query': query})


def child_detail(request, pk):
    child = get_object_or_404(Child.objects.select_related('district'), pk=pk)
    records = child.immunizations.select_related('vaccine', 'facility').order_by('date_given')
    return render(request, 'health_data/child_detail.html', {'child': child, 'records': records})


@login_required
def child_create(request):
    form = ChildForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        child = form.save()
        messages.success(request, f'{child.full_name} was registered.')
        return redirect('health_data:child_detail', pk=child.pk)
    return render(request, 'health_data/child_form.html', {'form': form, 'title': 'Register a child'})


@login_required
def child_update(request, pk):
    child = get_object_or_404(Child, pk=pk)
    form = ChildForm(request.POST or None, instance=child)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{child.full_name} was updated.')
        return redirect('health_data:child_detail', pk=child.pk)
    return render(request, 'health_data/child_form.html', {'form': form, 'title': f'Edit {child.full_name}'})


@login_required
def child_delete(request, pk):
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        name = child.full_name
        child.delete()
        messages.success(request, f'{name} was deleted.')
        return redirect('health_data:child_list')
    return render(request, 'health_data/child_confirm_delete.html', {'child': child})


def district_list(request):
    districts = District.objects.annotate(
        facility_total=Count('facilities', distinct=True),
        child_total=Count('children', distinct=True),
    )
    return render(request, 'health_data/district_list.html', {'districts': districts})


def district_detail(request, pk):
    district = get_object_or_404(District, pk=pk)
    today = date.today()
    rows = []
    for vaccine in Vaccine.objects.all():
        # only count children old enough to have received the first dose
        cutoff = today - timedelta(days=vaccine.recommended_age_months * 30)
        eligible = district.children.filter(date_of_birth__lte=cutoff).count()
        vaccinated = ImmunizationRecord.objects.filter(
            child__district=district,
            child__date_of_birth__lte=cutoff,
            vaccine=vaccine,
            dose_number=1,
        ).count()
        rate = round(100 * vaccinated / eligible, 1) if eligible else None
        rows.append({
            'vaccine': vaccine.name,
            'eligible': eligible,
            'vaccinated': vaccinated,
            'rate': rate,
            'below_target': rate is not None and rate < COVERAGE_TARGET,
        })
    context = {
        'district': district,
        'child_total': district.children.count(),
        'facility_total': district.facilities.count(),
        'rows': rows,
        'target': COVERAGE_TARGET,
    }
    return render(request, 'health_data/district_detail.html', context)


def facility_list(request):
    query = request.GET.get('q', '').strip()
    district_id = request.GET.get('district', '')
    facilities = HealthFacility.objects.select_related('district').annotate(
        immunization_total=Count('immunizations')
    )
    if query:
        facilities = facilities.filter(name__icontains=query)
    if district_id.isdigit():
        facilities = facilities.filter(district_id=int(district_id))
    page = Paginator(facilities, 25).get_page(request.GET.get('page'))
    context = {
        'page': page,
        'query': query,
        'district_id': district_id,
        'districts': District.objects.all(),
    }
    return render(request, 'health_data/facility_list.html', context)