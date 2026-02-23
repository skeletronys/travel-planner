from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from trips.models import TravelProject, ProjectPlace
from trips.serializers import (
    TravelProjectSerializer,
    TravelProjectCreateSerializer,
    ProjectPlaceSerializer,
    ProjectPlaceCreateSerializer,
    ProjectPlaceUpdateSerializer,
)
from trips.services import AICService, AICServiceError


class TravelProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"] # Without put
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["start_date"]
    ordering_fields = ["name", "start_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return TravelProject.objects.filter(user=self.request.user).prefetch_related("places")

    def get_serializer_class(self):
        if self.action == "create":
            return TravelProjectCreateSerializer
        return TravelProjectSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        external_ids = serializer.validated_data.pop("places", [])

        # Validate all external IDs against AIC before creating anything
        aic = AICService()
        artworks = []
        for ext_id in external_ids:
            try:
                artwork = aic.get_artwork(ext_id)
            except AICServiceError as e:
                return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            artworks.append(artwork)

        project = TravelProject.objects.create(user=request.user, **serializer.validated_data)

        for artwork in artworks:
            ProjectPlace.objects.create(
                project=project,
                external_id=artwork["id"],
                title=artwork["title"],
                artist=artwork.get("artist_display", ""),
                image_url=artwork.get("image_url", ""),
            )

        output = TravelProjectSerializer(project, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.has_visited_places:
            return Response(
                {"detail": "Cannot delete a project that has visited places."},
                status=status.HTTP_409_CONFLICT,
            )
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlacePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ProjectPlaceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_project(self, project_id, user):
        return get_object_or_404(TravelProject, pk=project_id, user=user)

    def get(self, request, project_id):
        project = self._get_project(project_id, request.user)
        queryset = project.places.all()

        visited = request.query_params.get("visited")
        if visited is not None:
            queryset = queryset.filter(visited=visited.lower() == "true")

        paginator = PlacePagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProjectPlaceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, project_id):
        project = self._get_project(project_id, request.user)

        if project.places.count() >= settings.MAX_PLACES_PER_PROJECT:
            return Response(
                {"detail": f"A project cannot have more than {settings.MAX_PLACES_PER_PROJECT} places."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ProjectPlaceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        external_id = serializer.validated_data["external_id"]
        notes = serializer.validated_data.get("notes", "")

        aic = AICService()
        try:
            artwork = aic.get_artwork(external_id)
        except AICServiceError as e:
            return Response({"detail": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            place = ProjectPlace.objects.create(
                project=project,
                external_id=artwork["id"],
                title=artwork["title"],
                artist=artwork.get("artist_display", ""),
                image_url=artwork.get("image_url", ""),
                notes=notes,
            )
        except IntegrityError:
            return Response(
                {"detail": "This place is already added to the project."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(ProjectPlaceSerializer(place).data, status=status.HTTP_201_CREATED)


class ProjectPlaceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_place(self, project_id, place_id, user):
        project = get_object_or_404(TravelProject, pk=project_id, user=user)
        return get_object_or_404(ProjectPlace, pk=place_id, project=project)

    def get(self, request, project_id, place_id):
        place = self._get_place(project_id, place_id, request.user)
        return Response(ProjectPlaceSerializer(place).data)

    def patch(self, request, project_id, place_id):
        place = self._get_place(project_id, place_id, request.user)
        serializer = ProjectPlaceUpdateSerializer(place, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProjectPlaceSerializer(place).data)
