from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TravelProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def has_visited_places(self) -> bool:
        return self.places.filter(visited=True).exists()


class ProjectPlace(models.Model):
    project = models.ForeignKey(TravelProject, on_delete=models.CASCADE, related_name="places")
    external_id = models.IntegerField()
    title = models.CharField(max_length=512)
    artist = models.CharField(max_length=512, blank=True, default="")
    image_url = models.URLField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    visited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["project", "external_id"], name="unique_place_per_project")
        ]

    def __str__(self):
        return f"{self.title} ({self.project.name})"
