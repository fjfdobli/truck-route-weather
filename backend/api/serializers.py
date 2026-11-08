from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

MAX_DAYS_AHEAD = 5


class PlaceSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=200)
    lat = serializers.FloatField(required=False, min_value=-90, max_value=90)
    lon = serializers.FloatField(required=False, min_value=-180, max_value=180)

    def validate(self, attrs):
        if ('lat' in attrs) != ('lon' in attrs):
            raise serializers.ValidationError('Send both lat and lon, or neither.')
        return attrs


class PlanRequestSerializer(serializers.Serializer):
    origin = PlaceSerializer()
    destination = PlaceSerializer()
    departure = serializers.DateTimeField()
    weight_lb = serializers.IntegerField(min_value=0, max_value=200_000)
    interval_mi = serializers.ChoiceField(choices=[10, 25, 50], default=25)

    def validate_departure(self, value):
        # The forecast runs about a week out, and the heatmap needs 48 hours after departure.
        now = timezone.now()
        if value < now - timedelta(hours=1):
            raise serializers.ValidationError('Departure is in the past.')
        if value > now + timedelta(days=MAX_DAYS_AHEAD):
            raise serializers.ValidationError(
                f'Departure must be within {MAX_DAYS_AHEAD} days; forecasts run out after that.'
            )
        return value
