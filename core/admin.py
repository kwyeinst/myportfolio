from django.contrib import admin
from django.utils.html import format_html

from .models import Achievement, Experience, Profile, Project

admin.site.site_header = "Portfolio admin"
admin.site.site_title = "Portfolio admin"
admin.site.index_title = "Manage your portfolio"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "tech", "featured", "sort_order", "updated_at")
    list_editable = ("category", "featured", "sort_order")
    list_filter = ("category", "featured")
    search_fields = ("title", "summary", "tech")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "period", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("title", "organization", "description", "bullets")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "year_only")
    date_hierarchy = "date"
    search_fields = ("title", "description")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ("photo", "preview", "resume", "resume_status", "about")
    readonly_fields = ("preview", "resume_status")
    list_display = ("__str__", "preview", "resume_status")

    def preview(self, obj):
        if obj and obj.photo:
            return format_html('<img src="{}" alt="Current photo" style="height:120px;width:120px;object-fit:cover;border-radius:50%">', obj.photo.url)
        return "No photo yet"

    def resume_status(self, obj):
        if obj and obj.resume:
            return format_html('<a href="{}" target="_blank" rel="noopener">View current resume (PDF)</a>', obj.resume.url)
        return "No resume uploaded yet"

    def has_add_permission(self, request):
        return not Profile.objects.exists() and super().has_add_permission(request)
