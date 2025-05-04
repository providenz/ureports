from django.contrib import admin
from .models import DataTable, TableDownload, RegionStatistic
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

class PhotoPresenceFilter(admin.SimpleListFilter):
    title = _('Photo Presence')
    parameter_name = 'photo_presence'

    def lookups(self, request, model_admin):
        return (
            ('has_photo', _('Has Photo')),
            ('no_photo', _('No Photo')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'has_photo':
            return queryset.exclude(photo__exact='')
        elif self.value() == 'no_photo':
            return queryset.filter(photo__exact='')

class DataTableAdmin(admin.ModelAdmin):
    list_display = (
        "gender",
        "display_photo",  # Replace "photo" with "display_photo"
        "age",
        "place",
        "project",
        "category",
    )
    list_filter = (
        "category",
        "project",
        PhotoPresenceFilter,
        "place",
        "gender",
        "age",
        "date",
    )
    search_fields = (
        "category",
        "gender",
        "age",
        "place",
        "project",
        "date",
    )

    def display_photo(self, obj):
        if obj.photo:
            return mark_safe('<img src="{url}" width="100" />'.format(url=obj.photo.url))
        else:
            return "No Photo"
    display_photo.short_description = 'Photo Preview'  # Sets the column heade

admin.site.register(TableDownload)
admin.site.register(DataTable, DataTableAdmin)
admin.site.register(RegionStatistic)
