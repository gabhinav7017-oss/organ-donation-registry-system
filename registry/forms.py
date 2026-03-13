from django import forms
from .models import Donor, Recipient, OrganMatch, ORGAN_CHOICES


class DonorForm(forms.ModelForm):
    organs = forms.MultipleChoiceField(
        choices=ORGAN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Organs Willing to Donate",
    )

    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'blood_type',
            'email', 'phone', 'address', 'organs', 'medical_notes', 'status',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_organs(self):
        return list(self.cleaned_data['organs'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and isinstance(self.instance.organs, list):
            self.initial['organs'] = self.instance.organs


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'blood_type',
            'email', 'phone', 'address', 'organ_needed', 'urgency',
            'medical_notes', 'status',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'organ_needed': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'medical_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class OrganMatchForm(forms.ModelForm):
    class Meta:
        model = OrganMatch
        fields = ['donor', 'recipient', 'organ', 'status', 'notes']
        widgets = {
            'donor': forms.Select(attrs={'class': 'form-select'}),
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'organ': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
