from rest_framework_gis.serializers import GeoModelSerializer
from .models import Spot

class SpotSerializer(GeoModelSerializer):
    class Meta:
        model = Spot
        geo_field = "location"
        fields = "__all__"
