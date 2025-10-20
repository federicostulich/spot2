from django.contrib.gis.db import models



class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Municipality(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="municipalities")
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        unique_together = [("name", "state")]
        indexes = [models.Index(fields=["name"], name="municipality_name_idx")]
        ordering = ["state__name", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.state.name})"


class Settlement(models.Model):
    name = models.CharField(max_length=255)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name="settlements")

    class Meta:
        unique_together = [("name", "municipality")]
        indexes = [models.Index(fields=["name"], name="settlement_name_idx")]
        ordering = ["municipality__state__name", "municipality__name", "name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.municipality.name}"



class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    geom = models.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Corridor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Spot(models.Model):
    class Sector(models.IntegerChoices):
        INDUSTRIAL = 9, "Industrial"
        OFFICE     = 11, "Office"
        RETAIL     = 12, "Retail"
        LAND       = 15, "Land"

    class Type(models.IntegerChoices):
        SINGLE   = 1, "Single"
        COMPLEX  = 2, "Complex"
        SUBSPACE = 3, "Subspace"

    class Modality(models.TextChoices):
        RENT      = "rent", "Rent"
        SALE      = "sale", "Sale"
        RENT_SALE = "rent_sale", "Rent & Sale"

    spot_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    location = models.PointField(srid=4326)

    settlement = models.ForeignKey(Settlement, null=True, blank=True, on_delete=models.SET_NULL, related_name="spots")
    region = models.ForeignKey(Region, null=True, blank=True, on_delete=models.SET_NULL, related_name="spots")
    corridor = models.ForeignKey(Corridor, null=True, blank=True, on_delete=models.SET_NULL, related_name="spots")

    address = models.CharField(max_length=512, blank=True)

    sector_id = models.IntegerField(choices=Sector.choices, null=True, blank=True)
    type_id = models.IntegerField(choices=Type.choices, null=True, blank=True)
    modality = models.CharField(max_length=20, choices=Modality.choices, default=Modality.RENT)

    area_sqm = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_sqm_rent_mxn = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_total_rent_mxn = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_sqm_sale_mxn = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    price_total_sale_mxn = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    maintenance_cost_mxn = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    user_id = models.CharField(max_length=64, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["location"], name="spot_point_idx"),
            models.Index(fields=["sector_id"], name="spot_sector_idx"),
            models.Index(fields=["type_id"], name="spot_type_idx"),
        ]
        ordering = ["spot_id"]

    def __str__(self) -> str:
        return f"{self.spot_id} - {self.title or ''}"
