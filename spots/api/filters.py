from django.db.models import QuerySet

def apply_spot_filters(qs: QuerySet, params) -> QuerySet:
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
        qs = qs.filter(settlement__municipality__name__iexact=municipality.strip())

    return qs
