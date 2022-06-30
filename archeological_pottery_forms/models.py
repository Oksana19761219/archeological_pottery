from django.db import models

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

    def __str__(self):
        return f"{self.author}, {self.title}, {self.report_year}"


class BibliographicReference(models.Model):
    reference = models.CharField(
        'bibliographic reference',
        max_length=200,
        help_text='enter a bibliographic reference (archive, document number, etc.)'
    )
    report = models.ForeignKey(
        'Bibliography',
        on_delete=models.SET_NULL,
        null=True
    )

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
        help_text='color of archaeological find'
    )
    lip_nr = models.ForeignKey(
        'PotteryLipShape',
        on_delete=models.SET_NULL,
        null=True
    )
    ornament_nr = models.ForeignKey(
        'PotteryOrnamentShape',
        on_delete=models.SET_NULL,
        null=True
    )
    note = models.CharField(
        'note',
        max_length=500,
        help_text='enter some text you need'
    )
    research_object_nr = models.IntegerField(
        'research object number',
        null=True,
        help_text="enter the research object number"
    )

    def __str__(self):
        return f"{self.find_registration_nr}, {self.research_object_nr}"
