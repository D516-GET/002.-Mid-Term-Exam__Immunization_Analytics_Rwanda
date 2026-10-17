from datetime import date, timedelta

from django import forms

from .models import Child


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['full_name', 'date_of_birth', 'sex', 'district']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        if dob > date.today():
            raise forms.ValidationError('Date of birth cannot be in the future.')
        if dob < date.today() - timedelta(days=365 * 5):
            raise forms.ValidationError('Registered children must be under 5 years old.')
        return dob