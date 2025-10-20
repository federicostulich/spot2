from rest_framework_gis.serializers import GeoModelSerializer
from rest_framework import serializers
from django.contrib.gis.geos import Polygon
from spots.models import Spot


class SpotSerializer(GeoModelSerializer):
    class Meta:
        model = Spot
        geo_field = "location"
        fields = "__all__"



class SpotListSerializer(GeoModelSerializer):
    class Meta:
        model = Spot
        geo_field = "location"
        fields = (
            "spot_id", "title", "sector_id", "type_id", "modality",
            "location", "area_sqm", "price_total_rent_mxn",
            "settlement", "region", "corridor",
        )

class SpotDetailSerializer(GeoModelSerializer):
    class Meta:
        model = Spot
        geo_field = "location"
        fields = "__all__"

class NearbyParamsSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=True)
    lng = serializers.FloatField(required=True)
    radius = serializers.FloatField(required=False, default=1000, min_value=0)

class WithinPolygonSerializer(serializers.Serializer):
    polygon = serializers.DictField()

    def validate_polygon(self, value):
        if not isinstance(value, dict) or value.get("type") != "Polygon":
            raise serializers.ValidationError("polygon.type debe ser 'Polygon'")
        coords = value.get("coordinates")
        if not coords or not isinstance(coords, list) or not coords[0]:
            raise serializers.ValidationError("polygon.coordinates inválidos")
        try:
            ring = [(float(x), float(y)) for x, y in coords[0]]
        except Exception:
            raise serializers.ValidationError("Coordenadas inválidas. Formato [[lng,lat],...]")
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        poly = Polygon(ring, srid=4326)
        return poly
