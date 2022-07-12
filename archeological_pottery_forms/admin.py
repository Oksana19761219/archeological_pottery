from django.contrib import admin
from .models import \
    Bibliography, \
    BibliographicReference, \
    PotteryLipShape, \
    PotteryOrnamentShape, \
    PotteryDescription, \
    ResearchObject, \
    PotteryMakingAction

# Register your models here.


class BibliographicReferenceInline(admin.TabularInline):
    model = BibliographicReference
    extra = 0
    can_delete = False


class BibliographyAdmin(admin.ModelAdmin):
    list_display = ('author',
                    'title',
                    'research_year',
                    'report_year',
                    'research_object',
                    'display_references')
    inlines = [BibliographicReferenceInline]
    search_fields = ('author',
                    'title',
                    'research_year',
                    'report_year',
                     'references__reference')


class BibliographicReferenceAdmin(admin.ModelAdmin):
    list_display = ('reference',)
    search_fields = ('reference',)


class PotteryDescriptionAdmin(admin.ModelAdmin):
    list_display = ('researcher',
                    'find_registration_nr',
                    'arc_length',
                    'color',
                    'lip',
                    'ornament',
                    'note',
                    'research_object',
                    'neck_nr')
    list_filter = ('lip',
                   'ornament')
    fieldsets = (
        ('General', {'fields': ('find_registration_nr', 'research_object', 'researcher')}),
        ('Description', {'fields': ('arc_length','color', 'lip', 'ornament', 'neck_nr')}),
        ('Note', {'fields': ('note',)}),
    )

class ResearchObjectAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'year',
                    'research_type')
    list_filter = ('research_type',)
    search_fields = ('name',
                    'year')


admin.site.register(Bibliography, BibliographyAdmin)
admin.site.register(BibliographicReference, BibliographicReferenceAdmin)
admin.site.register(PotteryLipShape)
admin.site.register(PotteryOrnamentShape)
admin.site.register(PotteryDescription, PotteryDescriptionAdmin)
admin.site.register(ResearchObject, ResearchObjectAdmin)
admin.site.register(PotteryMakingAction)

