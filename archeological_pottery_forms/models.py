from django.db import models

# Create your models here.

class Bibliography(models.Model):
    author = models.CharField(
        'Author',
        max_length=200,
        help_text="enter the author's name"
    )
    title = models.CharField(
        'Title',
        max_length=200,
        help_text="enter the title of the report"
    )
    research_year = models.CharField(
        'Research Year',
        max_length=20,
        help_text="enter the year of archaeological research"
    )
    report_year = models.CharField(
        'Report Year',
        max_length=20,
        help_text="enter the year of the research report"
    )
    research_object_nr = models.IntegerField(
        'Research Object Number',
        null=True,
        help_text="enter the research object number"
    )
    record_nr  = models.IntegerField(
        'Record Number',
        null=True,
        help_text="temporary field, ID from old database"
    )

    def __str__(self):
        return f"{self.author}, {self.title}, {self.report_year}"
