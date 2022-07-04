from django.db import models
from django.urls import reverse
# Create your models here.



class Bibliography(models.Model):
    author = models.CharField(
        'author',
        max_length=250,
        help_text="enter the author's name"
    )
    title = models.CharField(
        'title',
        max_length=700,
        help_text="enter the title of the report"
    )
    research_year = models.CharField(
        'research year',
        max_length=100,
        help_text="enter the year of archaeological research"
    )
    report_year = models.CharField(
        'report year',
        max_length=100,
        help_text="enter the year of the research report"
    )
    research_object_nr = models.IntegerField(
        'research object number',
        null=True,
        help_text="enter the research object number"
    )

    class Meta:
        ordering = ['report_year']
        verbose_name = 'report'
        verbose_name_plural = 'reports'

    def __str__(self):
        return f"{self.author}, {self.title}, {self.report_year}"

    def get_absolute_url(self):
        return reverse('bibliography', args=[str(self.id)])

    def display_references(self):
        return ', '.join(reference.reference for reference in self.references.all())

    display_references.short_description = 'references'


class BibliographicReference(models.Model):
    reference = models.CharField(
        'bibliographic reference',
        max_length=200,
        help_text='enter a bibliographic reference (archive, document number, etc.)'
    )
    report = models.ForeignKey(
        'Bibliography',
        on_delete=models.SET_NULL,
        null=True,
        related_name='references'
    )

    class Meta:
        ordering = ['reference']
        verbose_name = 'reference'
        verbose_name_plural = 'references'

    def __str__(self):
        return self.reference


class PotteryLipShape(models.Model):
    lip_form = models.ImageField(
        'Lip form',
        upload_to='images',
        null=True
    )
    lip_nr = models.IntegerField(
        'old lip number',
        null=True,
        help_text='temporary field, lip number from old database'
    )


class PotteryOrnamentShape(models.Model):
    ornament_form = models.ImageField(
        'ornament form',
        upload_to='images',
        null=True
    )
    ornament_nr = models.IntegerField(
        'old ornament number',
        null=True,
        help_text='temporary field, ornament number from old database'
    )


class PotteryDescription(models.Model):
    find_registration_nr = models.CharField(
        'registration number',
        max_length=20,
        help_text='enter the registration number of the archaeological find'
    )
    arc_length = models.IntegerField(
        'arc length',
        null=True,
        help_text='enter length of lip arc (milimeters)'
    )
    color = models.CharField(
        'color',
        max_length=10,
        null=True,
        help_text='color of archaeological find'
    )
    lip = models.ForeignKey(
        'PotteryLipShape',
        on_delete=models.SET_NULL,
        null=True,
        related_name='findings'
    )
    ornament = models.ForeignKey(
        'PotteryOrnamentShape',
        on_delete=models.SET_NULL,
        null=True,
        related_name='findings'
    )
    note = models.CharField(
        'note',
        max_length=500,
        null=True,
        help_text='enter some text you need'
    )
    research_object_nr = models.IntegerField(
        'research object number',
        null=True,
        help_text='enter research object number'
    )
    neck_nr = models.IntegerField(
        'neck number',
        null=True,
        help_text='temporary field, neck id from old database'
    )

    class Meta:
        ordering = ['research_object_nr', 'find_registration_nr']


    def __str__(self):
        return f"reg. nr.: {self.find_registration_nr}, research id: {self.research_object_nr}"

    def get_absolute_url(self):
        return reverse('findings', args=[str(self.id)])