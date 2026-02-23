from rest_framework import serializers
from trips.models import TravelProject, ProjectPlace


class ProjectPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = [
            "id", "external_id", "title", "artist",
            "image_url", "notes", "visited", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "external_id", "title", "artist", "image_url", "created_at", "updated_at"]


class ProjectPlaceCreateSerializer(serializers.Serializer):
    external_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ProjectPlaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = ["notes", "visited"]


class TravelProjectSerializer(serializers.ModelSerializer):
    places_count = serializers.SerializerMethodField()

    class Meta:
        model = TravelProject
        fields = ["id", "name", "description", "start_date", "places_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_places_count(self, obj):
        return obj.places.count()


class TravelProjectCreateSerializer(serializers.ModelSerializer):
    places = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        write_only=True,
        help_text="List of external AIC artwork IDs to import as places",
    )

    class Meta:
        model = TravelProject
        fields = ["name", "description", "start_date", "places"]

    def validate_places(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Cannot add more than 10 places to a project.")
        return value
