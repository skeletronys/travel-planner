from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trips.views import TravelProjectViewSet, ProjectPlaceListCreateView, ProjectPlaceDetailView

router = DefaultRouter()
router.register(r"projects", TravelProjectViewSet, basename="project")

urlpatterns = [
    path("projects/<int:project_id>/places/", ProjectPlaceListCreateView.as_view(), name="project-places"),
    path("projects/<int:project_id>/places/<int:place_id>/", ProjectPlaceDetailView.as_view(), name="project-place-detail"),
    path("", include(router.urls)),
]
