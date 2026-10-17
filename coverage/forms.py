from django import forms

from health_data.models import Child, HealthFacility

from .models import ImmunizationRecord


class ImmunizationRecordForm(forms.ModelForm):
    class Meta:
        model = ImmunizationRecord
        fields = ['child', 'vaccine', 'facility', 'dose_number', 'date_given']
        widgets = {
            'date_given': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['child'].queryset = Child.objects.select_related('district')
        self.fields['child'].label_from_instance = (
            lambda c: f'{c.full_name} ({c.date_of_birth}, {c.district.name})'
        )
        self.fields['facility'].queryset = HealthFacility.objects.select_related('district')
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'