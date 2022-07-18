from .models import PotteryDescription
from django import forms

class PotteryDescriptionForm(forms.ModelForm):
    find_registration_nr = forms.CharField(label='find registration nr: ', max_length=20)
    arc_length = forms.IntegerField(label='arc length', required=False)
    color = forms.CharField(label='color', max_length=10, required=False)
    lip_id = forms.IntegerField(label='lip id', required=False)
    ornament_id = forms.IntegerField(label='ornament id', required=False)
    note = forms.CharField(label='note', max_length=500, required=False)
    research_object_id = forms.IntegerField(label='research object id')

    class Meta:
        model = PotteryDescription
        fields = (
            'find_registration_nr',
            'arc_length',
            'color',
            'lip_id',
            'ornament_id',
            'note',
            'research_object_id',
        )
        # widgets = {'research_object': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(PotteryDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['find_registration_nr'].widget.attrs.update({'class': 'form-control'})
        self.fields['arc_length'].widget.attrs.update({'class': 'form-control'})
        self.fields['color'].widget.attrs.update({'class': 'form-control'})
        self.fields['lip_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['ornament_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['note'].widget.attrs.update({'class': 'form-control'})
        self.fields['research_object_id'].widget.attrs.update({'class': 'form-control'})


COLOR_CHOICES = (
    ('red', 'red'),
    ('green', 'green'),
    ('blue', 'blue'),
    ('black', 'black')
)

class DrawingForm(forms.Form):
    drawing = forms.ImageField(label='drawings', widget=forms.ClearableFileInput(attrs={'multiple': True}))
    frame_width = forms.IntegerField(label='frame width, mm')
    frame_height = forms.IntegerField(label='frame height, mm')
    frame_color = forms.ChoiceField(label='frame color', choices=COLOR_CHOICES)
    ceramic_color = forms.ChoiceField(label='ceramic color', choices=COLOR_CHOICES)

    def __init__(self, *args, **kwargs):
        super(DrawingForm, self).__init__(*args, **kwargs)
        self.fields['drawing'].widget.attrs.update({'class': 'form-control'})
        self.fields['frame_width'].widget.attrs.update({'class': 'form-control'})
        self.fields['frame_height'].widget.attrs.update({'class': 'form-control'})
        self.fields['frame_color'].widget.attrs.update({'class': 'form-control'})
        self.fields['ceramic_color'].widget.attrs.update({'class': 'form-control'})

