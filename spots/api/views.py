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
    NearbyParamsSerializer, WithinPolygonSerializer
)
from .filters import apply_spot_filters

class SpotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Spot.objects
        .select_related("settlement__municipality__state", "region", "corridor")
        .order_by("id")
    )
    def get_serializer_class(self):
        return SpotDetailSerializer if self.action == "retrieve" else SpotListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return apply_spot_filters(qs, self.request.query_params)

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

    @action(detail=False, methods=["post"], url_path="within")
    def within(self, request):
        s = WithinPolygonSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        polygon = s.validated_data["polygon"]

        qs = self.get_queryset().filter(location__within=polygon)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

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