from rest_framework import viewsets

from repository.models import Package
from repository.api.v1.serializers import (
    PackageSerializer,
)


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Package.objects
        .filter(is_active=True)
        .prefetch_related("versions")
    )
    serializer_class = PackageSerializer
    lookup_field = "uuid4"
