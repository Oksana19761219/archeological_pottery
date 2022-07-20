from .models import PotteryDescription
from django import forms

class PotteryDescriptionForm(forms.ModelForm):
    find_registration_nr = forms.CharField(label='radinio registracijos nr.', max_length=20)
    arc_length = forms.IntegerField(label='lanko ilgis', required=False)
    color = forms.CharField(label='spalva', max_length=10, required=False)
    lip_id = forms.IntegerField(label='lupos id', required=False)
    ornament_id = forms.IntegerField(label='ornamento id', required=False)
    note = forms.CharField(label='pastaba', max_length=500, required=False)

    class Meta:
        model = PotteryDescription
        fields = (
            'find_registration_nr',
            'arc_length',
            'color',
            'lip_id',
            'ornament_id',
            'note',
        )

    def __init__(self, *args, **kwargs):
        super(PotteryDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['find_registration_nr'].widget.attrs.update({'class': 'form-control'})
        self.fields['arc_length'].widget.attrs.update({'class': 'form-control'})
        self.fields['color'].widget.attrs.update({'class': 'form-control'})
        self.fields['lip_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['ornament_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['note'].widget.attrs.update({'class': 'form-control'})


COLOR_CHOICES = (
    ('red', 'raudona'),
    ('green', 'žalia'),
    ('blue', 'mėlyna'),
    ('black', 'juoda')
)

ORIENTATION_CHOICES = (
    ('left', 'kairė'),
    ('right', 'dešinė')
)

class DrawingForm(forms.Form):
    drawing = forms.ImageField(label='brėžiniai', widget=forms.ClearableFileInput(attrs={'multiple': True}))
    frame_width = forms.IntegerField(label='rėmo plotis, mm')
    frame_height = forms.IntegerField(label='rėmo aukštis, mm')
    frame_color = forms.ChoiceField(label='rėmo spalva', choices=COLOR_CHOICES)
    ceramic_color = forms.ChoiceField(label='radinio profilio spalva', choices=COLOR_CHOICES)
    ceramic_orientation = forms.ChoiceField(label='radinio orientacija brėžinyje', choices=ORIENTATION_CHOICES)

    def __init__(self, *args, **kwargs):
        super(DrawingForm, self).__init__(*args, **kwargs)
        self.fields['drawing'].widget.attrs.update({'class': 'btn btn-light'})
        self.fields['frame_width'].widget.attrs.update({'class': 'form-control'})
        self.fields['frame_height'].widget.attrs.update({'class': 'form-control'})
        self.fields['frame_color'].widget.attrs.update({'class': 'form-control'})
        self.fields['ceramic_color'].widget.attrs.update({'class': 'form-control'})
        self.fields['ceramic_orientation'].widget.attrs.update({'class': 'form-control'})

