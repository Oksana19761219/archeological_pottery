from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from tinymce.models import HTMLField
from math import  pi
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
    research_object = models.ForeignKey(
        'ResearchObject',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports'
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


class PotteryMakingAction(models.Model):
    action = models.CharField(
        'action',
        max_length=200
    )
    sequence = models.IntegerField(
        'sequence',
        null=True
    )

    class Meta:
        ordering = ['sequence', 'action']

    def __str__(self):
        return self.action


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
    relative_lip = models.IntegerField(
        'relative_lip',
        null=True
    )
    note = models.CharField(
        'note',
        max_length=255,
        null=True,
        blank=True
    )
    action = models.ManyToManyField(PotteryMakingAction)


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
    relative_ornament = models.IntegerField(
        'relative_ornament',
        null=True
    )
    note = models.CharField(
        'note',
        max_length=255,
        null=True,
        blank=True
    )
    action = models.ManyToManyField(PotteryMakingAction)


class ContourGroup(models.Model):
    note = models.CharField(
        'note',
        max_length=255,
        null=True,
        blank=True
    )
    correlation_x = models.FloatField(
        'correlation_x',
        null=False,
        blank=False
    )
    precision = models.FloatField(
        'precision',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'group correlation: {self.correlation_x}'


class PotteryDescription(models.Model):
    find_registration_nr = models.CharField(
        'registration number',
        max_length=20,
        help_text='enter the registration number of the archaeological find'
    )
    arc_length = models.IntegerField(
        'arc length',
        null=True,
        blank=True,
        help_text='enter length of lip arc (milimeters)'
    )

    color = models.CharField(
        'color',
        max_length=10,
        null=True,
        blank=True,
        help_text='color of archaeological find'
    )
    lip = models.ForeignKey(
        'PotteryLipShape',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='findings'
    )
    ornament = models.ForeignKey(
        'PotteryOrnamentShape',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='findings'
    )
    note = models.CharField(
        'note',
        max_length=500,
        null=True,
        blank=True,
        help_text='enter some text you need'
    )
    research_object = models.ForeignKey(
        'ResearchObject',
        on_delete=models.SET_NULL,
        null=True,
        related_name='findings'
    )
    researcher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    profile_reviewed = models.BooleanField(
        'profile reviewed',
        default=False
    )
    correlation_calculated = models.BooleanField(
        'correlation_calculated',
        default=False
    )
    arc_angle = models.FloatField(
        'arc angle',
        null=True,
        blank=True
    )
    find_length = models.FloatField(
        'find length',
        null=True,
        blank=True
    )
    lip_base_y = models.IntegerField(
        'lip_base_y',
        null=True,
        blank=True
    )
    neck_min_y = models.IntegerField(
        'neck_min_y',
        null=True,
        blank=True
    )
    neck_max_y = models.IntegerField(
        'neck_max_y',
        null=True,
        blank=True
    )
    shoulders_min_y = models.IntegerField(
        'shoulders_min_y',
        null=True,
        blank=True
    )
    shoulders_max_y = models.IntegerField(
        'shoulders_max_y',
        null=True,
        blank=True
    )
    bottom_exist = models.BooleanField(
        'bottom_exist',
        default=False
    )
    neck_shoulders_union = models.CharField(
        'neck_shoulders_union',
        max_length=50,
        null=True,
        blank=True
    )
    shoulders_body_union = models.CharField(
        'shoulders_body_union',
        max_length=50,
        null=True,
        blank=True
    )
    neck_type = models.CharField(
        'neck_type',
        max_length=50,
        null=True,
        blank=True
    )
    shoulders_type = models.CharField(
        'shoulders_type',
        max_length=50,
        null=True,
        blank=True
    )
    neck_slope = models.FloatField(
        'neck_slope',
        null=True,
        blank=True
    )
    shoulders_slope = models.FloatField(
        'shoulders_slope',
        null=True,
        blank=True
    )
    width_avg = models.FloatField(
        'width_avg',
        null=True,
        blank=True
    )

    groups = models.ManyToManyField(ContourGroup)

    class Meta:
        ordering = ['research_object', 'find_registration_nr']

    def __str__(self):
        return f"reg. nr.: {self.find_registration_nr}, {self.research_object}"

    def get_absolute_url(self):
        return reverse('pottery_description', args=[str(self.id)])

    @property
    def top_mid_point(self):
        return CeramicContour.objects.filter(Q(find_id=self.id) & Q(y=0)).aggregate(Avg('x'))['x__avg']


class ResearchObject(models.Model):
    research_object_nr = models.IntegerField(
        'research object number',
        null=True,
        help_text='temporary field, object id from old database'
    )
    name = models.CharField(
        'title',
        max_length=500,
        help_text='name of research object, object description'
    )
    year = models.CharField(
        'year',
        max_length=50,
        help_text="enter the year of archaeological research"
    )
    research_type = models.CharField(
        'research type',
        max_length=250
    )
    description = HTMLField(
        'description',
        null=True,
        blank=True
    )

    class Meta:
        ordering=['year', 'research_type']
        verbose_name = 'research object'
        verbose_name_plural = 'research objects'

    def __str__(self):
        return f'{self.name}, {self.year}, {self.research_type}'



class CeramicContour(models.Model):
    x = models.IntegerField(
        'x',
        null=False,
        blank=False
    )

    y = models.IntegerField(
        'y',
        null=False,
        blank=False
    )

    find = models.ForeignKey(
        'PotteryDescription',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='coordinates'
    )

    curvature=models.FloatField(
        'curvature',
        null=True,
        blank=True
    )

    profile_side = models.CharField(
        'profile_side',
        max_length=10,
        null=True,
        blank=True
    )

    @property
    def x_canvas_middle(self):
        top_mid_point = CeramicContour.objects.filter(Q(find_id=self.find_id) & Q(y=0)).aggregate(Avg('x'))['x__avg']
        canvas_middle = 500 # canvas middle point if zoom == 0.5,0.5
        return self.x - top_mid_point + canvas_middle



class ContourCorrelation(models.Model):
    find_1 = models.IntegerField(
        'find_1',
        null=False,
        blank=False
    )
    find_2 = models.IntegerField(
        'find_2',
        null=False,
        blank=False
    )
    correlation_x = models.FloatField(
        'correlation_x',
        null=True,
        blank=True
    )
    correlation_width = models.FloatField(
        'correlation_width',
        null=True,
        blank=True
    )
    correlation_curvature = models.FloatField(
        'correlation_curvature',
        null=True,
        blank=True
    )
    length_compared = models.FloatField(
        'length_compared',
        null=True,
        blank=True
    )
    area = models.FloatField(
        'area',
        null=True,
        blank=True
    )
