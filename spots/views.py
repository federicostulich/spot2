from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Spot
from .serializers import SpotSerializer

@api_view(["GET"])
def health(request):
    """
    Simple health check endpoint.
    GET /api/health/
    """
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


class SpotViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = (
        Spot.objects
        .select_related(
            "settlement__municipality__state", "region", "corridor"
        )
        .order_by("id")
    )
    serializer_class = SpotSerializer
