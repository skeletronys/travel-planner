from django.contrib import admin
from .models import TravelProject, ProjectPlace


@admin.register(TravelProject)
class TravelProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "start_date", "created_at"]
    list_filter = ["start_date"]
    search_fields = ["name", "user__username"]


@admin.register(ProjectPlace)
class ProjectPlaceAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "external_id", "visited", "created_at"]
    list_filter = ["visited"]
    search_fields = ["title", "artist"]
