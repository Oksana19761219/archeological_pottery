from .models import PotteryDescription
from django import forms

class PotteryDescriptionForm(forms.ModelForm):


    class Meta:
        model = PotteryDescription
        fields = (
            'find_registration_nr',
            'arc_length',
            'color',
            'lip',
            'ornament',
            'note',
            'research_object',
        )
        widgets = {'research_object': forms.HiddenInput()}