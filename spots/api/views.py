from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from spots.models import Spot
from .serializers import (
    SpotListSerializer, SpotDetailSerializer,
    NearbyParamsSerializer, SpotSerializer, WithinPolygonSerializer
)
from .filters import apply_spot_filters
from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes, OpenApiResponse
)

class SpotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Spot.objects
        .select_related("settlement__municipality__state", "region", "corridor")
        .order_by("spot_id")
    )
    serializer_class = SpotSerializer
    lookup_field = "spot_id"
    lookup_value_regex = r"\d+"
    
    def get_serializer_class(self):
        return SpotDetailSerializer if self.action == "retrieve" else SpotListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return apply_spot_filters(qs, self.request.query_params)

    @extend_schema(
        description="Spots cercanos ordenados por distancia (metros).",
        parameters=[
            OpenApiParameter(name="lat", type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="lng", type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="radius", type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY, required=False,
                             description="Radio en metros (default 1000)"),
            OpenApiParameter(name="sector", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="type", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="municipality", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        ],
        responses={200: SpotSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Ejemplo",
                value={"count": 2, "next": None, "previous": None, "results": [
                    {"spot_id": 101, "title": "A", "location": {"type":"Point","coordinates":[-99.2,19.4]}},
                    {"spot_id": 102, "title": "B", "location": {"type":"Point","coordinates":[-99.21,19.41]}},
                ]},
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="nearby")
    def nearby(self, request):
        params = NearbyParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        lat = params.validated_data["lat"]
        lng = params.validated_data["lng"]
        radius = params.validated_data["radius"]

        p = Point(lng, lat, srid=4326)
        qs = (
            self.get_queryset()
            .annotate(distance=Distance("location", p))
            .filter(location__distance_lte=(p, D(m=radius)))
            .order_by("distance", "id")
        )

        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @extend_schema(
        description="Spots dentro de un polígono GeoJSON (SRID=4326).",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "polygon": {
                        "type": "object",
                        "example": {
                            "type": "Polygon",
                            "coordinates": [[
                                [-99.25, 19.35], [-99.25, 19.41],
                                [-99.18, 19.41], [-99.18, 19.35]
                            ]]
                        },
                    }
                },
                "required": ["polygon"],
            }
        },
        responses={200: SpotSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="within")
    def within(self, request):
        s = WithinPolygonSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        polygon = s.validated_data["polygon"]

        qs = self.get_queryset().filter(location__within=polygon)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @extend_schema(
        description="Promedio de `price_total_rent_mxn` por sector. Respeta filtros de la lista.",
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=False, methods=["get"], url_path="average-price-by-sector")
    def average_price_by_sector(self, request):
        qs = (
            self.get_queryset()
            .exclude(price_total_rent_mxn__isnull=True)
        )

        data = (
            qs.values("sector_id")
              .annotate(average_price_total_rent_mxn=Avg("price_total_rent_mxn"))
              .order_by("sector_id")
        )
        sector_labels = dict(Spot.Sector.choices)
        results = [
            {
                "sector_id": row["sector_id"],
                "sector_label": sector_labels.get(row["sector_id"], str(row["sector_id"])),
                "average_price_total_rent_mxn": row["average_price_total_rent_mxn"],
            }
            for row in data
        ]
        return Response(results)
    
    @extend_schema(
        description="Ranking por `price_total_rent_mxn` descendente. Respeta filtros de la lista.",
        parameters=[
            OpenApiParameter(name="limit", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False,
                             description="Cantidad máxima (1..100). Default: 10"),
            OpenApiParameter(name="sector", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="type", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="municipality", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        ],
        responses={200: SpotSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="top-rent")
    def top_rent(self, request):
        limit = request.query_params.get("limit", "10")
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 100))

        qs = (
            self.get_queryset()
            .exclude(price_total_rent_mxn__isnull=True)
            .order_by("-price_total_rent_mxn", "spot_id")
        )[:limit]

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)
