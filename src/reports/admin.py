from django.contrib import admin
from reports.models import Project, Category, Dashboard, UpdateDashboard


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "goal", "start_date", "end_date")
    search_fields = ("name",)
    filter_horizontal = (
        "donors",
        "categories",
    )  # Adding categories to the horizontal filter
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Dashboard)
admin.site.register(UpdateDashboard)
