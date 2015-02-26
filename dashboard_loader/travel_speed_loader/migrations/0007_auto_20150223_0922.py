# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_update_roads(apps, schema_editor):
    Road = apps.get_model("travel_speed_loader", "Road")
    try:
        m1 = Road.objects.get(name="M1")
    except Road.DoesNotExist:
        m1 = Road(name="M1")
    m1.am_direction="S"
    m1.pm_direction="N"
    m1.save()
    try:
        m2 = Road.objects.get(name="M2")
    except Road.DoesNotExist:
        m2 = Road(name="M2")
    m2.am_direction="E"
    m2.pm_direction="W"
    m2.save()
    try:
        m4 = Road.objects.get(name="M4")
    except Road.DoesNotExist:
        m4 = Road(name="M4")
    m4.am_direction="E"
    m4.pm_direction="W"
    m4.save()
    try:
        m7 = Road.objects.get(name="M7")
    except Road.DoesNotExist:
        m7 = Road(name="M7")
    m7.am_direction="NS"
    m7.pm_direction="NS"
    m7.save()
    Road.objects.exclude(name__in=["M1", "M2", "M4", "M7"]).delete()

def create_road_sections(apps, schema_editor):
    Road = apps.get_model("travel_speed_loader", "Road")
    RoadSection = apps.get_model("travel_speed_loader", "RoadSection")
    RoadSection.objects.all().delete()
    sections = [
        {"origin": "Ourimbah", "direction": "N-E", "destination": "Wyong", "label": "N7", "length": 6, "sort_order": 107, "route_direction": "N", "road": "M1"},
        {"origin": "Berowra", "direction": "S-W", "destination": "Wahroonga", "label": "S10", "length": 10, "sort_order": 210, "route_direction": "S", "road": "M1"},
        {"origin": "Gosford", "direction": "N-E", "destination": "Ourimbah", "label": "N6", "length": 13, "sort_order": 106, "route_direction": "N", "road": "M1"},
        {"origin": "Toukley", "direction": "N-E", "destination": "Morisset", "label": "N9", "length": 14, "sort_order": 109, "route_direction": "N", "road": "M1"},
        {"origin": "Wyong", "direction": "N-E", "destination": "Toukley", "label": "N8", "length": 9, "sort_order": 108, "route_direction": "N", "road": "M1"},
        {"origin": "Morisset", "direction": "N-E", "destination": "Toronto", "label": "N10", "length": 17, "sort_order": 110, "route_direction": "N", "road": "M1"},
        {"origin": "Toronto", "direction": "N-E", "destination": "Newcastle", "label": "N11", "length": 14, "sort_order": 111, "route_direction": "N", "road": "M1"},
        {"origin": "Wahroonga", "direction": "N", "destination": "Newcastle", "label": "NTOTAL", "length": 117, "sort_order": 199, "route_direction": "N", "road": "M1"},
        {"origin": "Toronto", "direction": "S-W", "destination": "Morisset", "label": "S2", "length": 17, "sort_order": 202, "route_direction": "S", "road": "M1"},
        {"origin": "Newcastle", "direction": "S-W", "destination": "Toronto", "label": "S1", "length": 14, "sort_order": 201, "route_direction": "S", "road": "M1"},
        {"origin": "Wahroonga", "direction": "N-E", "destination": "Mt Colah", "label": "N1", "length": 4, "sort_order": 101, "route_direction": "N", "road": "M1"},
        {"origin": "Berowra", "direction": "N-E", "destination": "Mooney Mooney", "label": "N3", "length": 14, "sort_order": 103, "route_direction": "N", "road": "M1"},
        {"origin": "Mt Colah", "direction": "N-E", "destination": "Berowra", "label": "N2", "length": 6, "sort_order": 102, "route_direction": "N", "road": "M1"},
        {"origin": "Mt White", "direction": "N-E", "destination": "Gosford", "label": "N5", "length": 12, "sort_order": 105, "route_direction": "N", "road": "M1"},
        {"origin": "Mooney Mooney", "direction": "N-E", "destination": "Mt White", "label": "N4", "length": 8, "sort_order": 104, "route_direction": "N", "road": "M1"},
        {"origin": "Morisset", "direction": "S-W", "destination": "Toukley", "label": "S3", "length": 14, "sort_order": 203, "route_direction": "S", "road": "M1"},
        {"origin": "Toukley", "direction": "S-W", "destination": "Wyong", "label": "S4", "length": 9, "sort_order": 204, "route_direction": "S", "road": "M1"},
        {"origin": "Wyong", "direction": "S-W", "destination": "Ourimbah", "label": "S5", "length": 6, "sort_order": 205, "route_direction": "S", "road": "M1"},
        {"origin": "Ourimbah", "direction": "S-W", "destination": "Gosford", "label": "S6", "length": 13, "sort_order": 206, "route_direction": "S", "road": "M1"},
        {"origin": "Gosford", "direction": "S-W", "destination": "Mt White", "label": "S7", "length": 12, "sort_order": 207, "route_direction": "S", "road": "M1"},
        {"origin": "Mt White", "direction": "S-W", "destination": "Mooney Mooney", "label": "S8", "length": 8, "sort_order": 208, "route_direction": "S", "road": "M1"},
        {"origin": "Mooney Mooney", "direction": "S-W", "destination": "Berowra", "label": "S9", "length": 14, "sort_order": 209, "route_direction": "S", "road": "M1"},
        {"origin": "Newcastle", "direction": "S", "destination": "Wahroonga", "label": "STOTAL", "length": 117, "sort_order": 299, "route_direction": "S", "road": "M1"},
        {"origin": "Windsor Rd", "direction": "W", "destination": "M7", "label": "W5", "length": 3, "sort_order": 305, "route_direction": "W", "road": "M2"},
        {"origin": "Beecroft Rd", "direction": "W", "destination": "Pennant Hills Rd", "label": "W3", "length": 2, "sort_order": 303, "route_direction": "W", "road": "M2"},
        {"origin": "Pennant Hills Rd", "direction": "W", "destination": "Windsor Rd", "label": "W4", "length": 5, "sort_order": 304, "route_direction": "W", "road": "M2"},
        {"origin": "Lane Cove Tunnel", "direction": "N-W", "destination": "Herring Road", "label": "W1", "length": 3, "sort_order": 301, "route_direction": "W", "road": "M2"},
        {"origin": "Herring Rd", "direction": "N-W", "destination": "Beecroft Rd", "label": "W2", "length": 5, "sort_order": 302, "route_direction": "W", "road": "M2"},
        {"origin": "Lane Cove Rd", "direction": "S-E", "destination": "Delhi Rd", "label": "E5", "length": 1, "sort_order": 405, "route_direction": "E", "road": "M2"},
        {"origin": "Delhi Rd", "direction": "S-E", "destination": "Lane Cove Tunnel", "label": "E6", "length": 1, "sort_order": 406, "route_direction": "E", "road": "M2"},
        {"origin": "Lane Cove Tunnel", "direction": "W", "destination": "M7", "label": "WTOTAL", "length": 18, "sort_order": 399, "route_direction": "W", "road": "M2"},
        {"origin": "M7", "direction": "E", "destination": "Lane Cove Tunnel", "label": "ETOTAL", "length": 18, "sort_order": 499, "route_direction": "E", "road": "M2"},
        {"origin": "Windsor Rd", "direction": "E", "destination": "Pennant Hills Rd", "label": "E2", "length": 5, "sort_order": 402, "route_direction": "E", "road": "M2"},
        {"origin": "M7", "direction": "S-E", "destination": "Windsor Rd", "label": "E1", "length": 3, "sort_order": 401, "route_direction": "E", "road": "M2"},
        {"origin": "Christie Rd", "direction": "S-E", "destination": "Lane Cove Rd", "label": "E4", "length": 1, "sort_order": 404, "route_direction": "E", "road": "M2"},
        {"origin": "Pennant Hills Rd", "direction": "E", "destination": "Christie Rd", "label": "E3", "length": 7, "sort_order": 403, "route_direction": "E", "road": "M2"},
        {"origin": "Prospect Hwy", "direction": "W", "destination": "M7", "label": "W5", "length": 4, "sort_order": 305, "route_direction": "W", "road": "M4"},
        {"origin": "M7", "direction": "W", "destination": "Roper Rd", "label": "W6", "length": 4, "sort_order": 306, "route_direction": "W", "road": "M4"},
        {"origin": "James Ruse Dr", "direction": "W", "destination": "Cumberland Hwy", "label": "W3", "length": 7, "sort_order": 303, "route_direction": "W", "road": "M4"},
        {"origin": "Cumberland Hwy", "direction": "W", "destination": "Prospect Hwy", "label": "W4", "length": 5, "sort_order": 304, "route_direction": "W", "road": "M4"},
        {"origin": "Concord Rd", "direction": "W", "destination": "Homebush Bay Dr", "label": "W1", "length": 2, "sort_order": 301, "route_direction": "W", "road": "M4"},
        {"origin": "Homebush Bay Dr", "direction": "W", "destination": "James Ruse Dr", "label": "W2", "length": 6, "sort_order": 302, "route_direction": "W", "road": "M4"},
        {"origin": "M7", "direction": "E", "destination": "Prospect Hwy", "label": "E5", "length": 4, "sort_order": 405, "route_direction": "E", "road": "M4"},
        {"origin": "Prospect Hwy", "direction": "E", "destination": "Cumberland Hwy", "label": "E6", "length": 5, "sort_order": 406, "route_direction": "E", "road": "M4"},
        {"origin": "Cumberland Hwy", "direction": "E", "destination": "James Ruse Dr", "label": "E7", "length": 7, "sort_order": 407, "route_direction": "E", "road": "M4"},
        {"origin": "James Ruse Dr", "direction": "E", "destination": "Homebush Bay Dr", "label": "E8", "length": 6, "sort_order": 408, "route_direction": "E", "road": "M4"},
        {"origin": "Homebush Bay Dr", "direction": "E", "destination": "Concord Rd", "label": "E9", "length": 2, "sort_order": 409, "route_direction": "E", "road": "M4"},
        {"origin": "Russell St", "direction": "E", "destination": "Concord Rd", "label": "ETOTAL", "length": 42, "sort_order": 499, "route_direction": "E", "road": "M4"},
        {"origin": "Concord Rd", "direction": "W", "destination": "Russell St", "label": "WTOTAL", "length": 42, "sort_order": 399, "route_direction": "W", "road": "M4"},
        {"origin": "The Northern Rd", "direction": "E", "destination": "Mamre Rd", "label": "E2", "length": 4, "sort_order": 402, "route_direction": "E", "road": "M4"},
        {"origin": "Russell St", "direction": "E", "destination": "The Northern Rd", "label": "E1", "length": 6, "sort_order": 401, "route_direction": "E", "road": "M4"},
        {"origin": "Roper Rd", "direction": "E", "destination": "M7", "label": "E4", "length": 4, "sort_order": 404, "route_direction": "E", "road": "M4"},
        {"origin": "Mamre Rd", "direction": "E", "destination": "Roper Rd", "label": "E3", "length": 4, "sort_order": 403, "route_direction": "E", "road": "M4"},
        {"origin": "Mamre Rd", "direction": "W", "destination": "The Northern Rd", "label": "W8", "length": 4, "sort_order": 308, "route_direction": "W", "road": "M4"},
        {"origin": "Roper Rd", "direction": "W", "destination": "Mamre Rd", "label": "W7", "length": 4, "sort_order": 307, "route_direction": "W", "road": "M4"},
        {"origin": "The Northern Rd", "direction": "W", "destination": "Russell St", "label": "W9", "length": 6, "sort_order": 309, "route_direction": "W", "road": "M4"},
        {"origin": "Sunnyholt Rd", "direction": "SE", "destination": "M2", "label": "N7", "length": 5, "sort_order": 107, "route_direction": "N", "road": "M7"},
        {"origin": "Richmond Rd", "direction": "N", "destination": "Sunnyholt Rd", "label": "N6", "length": 7, "sort_order": 106, "route_direction": "N", "road": "M7"},
        {"origin": "M5", "direction": "N", "destination": "M2", "label": "NTOTAL", "length": 40, "sort_order": 199, "route_direction": "N", "road": "M7"},
        {"origin": "Sunnyholt Rd", "direction": "NW", "destination": "Richmond Rd", "label": "S2", "length": 7, "sort_order": 202, "route_direction": "S", "road": "M7"},
        {"origin": "M2", "direction": "NW", "destination": "Sunnyholt Rd", "label": "S1", "length": 5, "sort_order": 201, "route_direction": "S", "road": "M7"},
        {"origin": "M5", "direction": "N", "destination": "Cowpasture Rd", "label": "N1", "length": 4, "sort_order": 101, "route_direction": "N", "road": "M7"},
        {"origin": "Elizabeth Dr", "direction": "N", "destination": "The Horsley Dr", "label": "N3", "length": 5, "sort_order": 103, "route_direction": "N", "road": "M7"},
        {"origin": "Cowpasture Rd", "direction": "N", "destination": "Elizabeth Dr", "label": "N2", "length": 6, "sort_order": 102, "route_direction": "N", "road": "M7"},
        {"origin": "M4", "direction": "N", "destination": "Richmond Rd", "label": "N5", "length": 7, "sort_order": 105, "route_direction": "N", "road": "M7"},
        {"origin": "The Horsley Dr", "direction": "N", "destination": "M4", "label": "N4", "length": 6, "sort_order": 104, "route_direction": "N", "road": "M7"},
        {"origin": "Richmond Rd", "direction": "S", "destination": "M4", "label": "S3", "length": 7, "sort_order": 203, "route_direction": "S", "road": "M7"},
        {"origin": "M4", "direction": "S", "destination": "The Horsley Dr", "label": "S4", "length": 6, "sort_order": 204, "route_direction": "S", "road": "M7"},
        {"origin": "The Horsley Dr", "direction": "S", "destination": "Elizabeth Dr", "label": "S5", "length": 5, "sort_order": 205, "route_direction": "S", "road": "M7"},
        {"origin": "Elizabeth Dr", "direction": "S", "destination": "Cowpasture Rd", "label": "S6", "length": 6, "sort_order": 206, "route_direction": "S", "road": "M7"},
        {"origin": "Cowpasture Rd", "direction": "S", "destination": "M5", "label": "S7", "length": 4, "sort_order": 207, "route_direction": "S", "road": "M7"},
        {"origin": "M2", "direction": "S", "destination": "M5", "label": "STOTAL", "length": 40, "sort_order": 299, "route_direction": "S", "road": "M7"},
    ]
    for section in sections:
        rs = RoadSection(origin=section["origin"],
                        direction=section["direction"],
                        destination=section["destination"],
                        label=section["label"],
                        length=section["length"],
                        sort_order=section["sort_order"],
                        route_direction=section["route_direction"])
        rs.road = Road.objects.get(name=section["road"])
        rs.save()

class Migration(migrations.Migration):

    dependencies = [
        ('travel_speed_loader', '0006_auto_20150223_0919'),
    ]

    operations = [
        migrations.RunPython(create_update_roads),
        migrations.RunPython(create_road_sections),
    ]

