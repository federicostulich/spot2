from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import Spot
from .serializers import SpotSerializer

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


class SpotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Spot.objects
        .select_related(
            "settlement__municipality__state",
            "region",
            "corridor",
        )
        .order_by("id")
    )
    serializer_class = SpotSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        sector = params.get("sector")
        type_ = params.get("type")
        municipality = params.get("municipality")

        if sector:
            try:
                qs = qs.filter(sector_id=int(sector))
            except ValueError:
                pass

        if type_:
            try:
                qs = qs.filter(type_id=int(type_))
            except ValueError:
                pass

        if municipality:
            qs = qs.filter(
                settlement__municipality__name__iexact=municipality.strip()
            )

        return qs

    @action(detail=False, methods=["get"], url_path="nearby")
    def nearby(self, request):

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = request.query_params.get("radius", "1000")

        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
        except (TypeError, ValueError):
            return Response(
                {"detail": "lat y lng son obligatorios y numéricos; radius en metros (numérico)."},
                status=400,
            )

        p = Point(lng, lat, srid=4326)

        qs = (
            self.get_queryset()
            .annotate(distance=Distance("location", p))
            .filter(location__distance_lte=(p, D(m=radius)))
            .order_by("distance", "id")
        )

        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)

