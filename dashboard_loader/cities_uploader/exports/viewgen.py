from widget_def.models import WidgetView, ViewProperty, ViewType, WidgetDefinition, Parametisation, ViewWidgetDeclaration

sa4s = [
    (101,"Capital Region", "capital_region", "NSW"),
    (102,"Central Coast", "central_coast", "NSW"),
    (103,"Central West", "central_west", "NSW"),
    (104,"Coffs Harbour - Grafton", "coffs_harbour", "NSW"),
    (105,"Far West and Orana", "far_west_nsw", "NSW"),
    (106,"Hunter Valley exc Newcastle", "hunter_valley", "NSW"),
    (107,"Illawarra", "illawarra", "NSW"),
    (108,"Mid North Coast", "mid_north_coast", "NSW"),
    (109,"Murray", "murray", "NSW"),
    (110,"New England and North West", "new_england", "NSW"),
    (111,"Newcastle and Lake Macquarie", "newcastle", "NSW"),
    (112,"Richmond - Tweed", "richmond", "NSW"),
    (113,"Riverina", "riverina", "NSW"),
    (114,"Southern Highlands and Shoalhaven", "southern_highlands", "NSW"),
    (115,"Sydney - Baulkham Hills and Hawkesbury", "baulkham_hills", "NSW"),
    (116,"Sydney - Blacktown", "blacktown", "NSW"),
    (117,"Sydney - City and Inner South", "sydney_inner_south", "NSW"),
    (118,"Sydney - Eastern Suburbs", "eastern_sydney", "NSW"),
    (119,"Sydney - Inner South West", "inner_sw_sydney", "NSW"),
    (120,"Sydney - Inner West", "inner_west_sydney", "NSW"),
    (121,"Sydney - North Sydney and Hornsby", "north_sydney", "NSW"),
    (122,"Sydney - Northern Beaches", "northern_beaches", "NSW"),
    (123,"Sydney - Outer South West", "outer_sw_sydney", "NSW"),
    (124,"Sydney - Outer West and Blue Mountains", "outer_west_sydney", "NSW"),
    (125,"Sydney - Parramatta", "parramatta", "NSW"),
    (126,"Sydney - Ryde", "ryde", "NSW"),
    (127,"Sydney - South West", "sw_sydney", "NSW"),
    (128,"Sydney - Sutherland", "sutherland", "NSW"),
    (201,"Ballarat", "ballarat", "Vic"),
    (202,"Bendigo", "bendigo", "Vic"),
    (203,"Geelong", "geelong", "Vic"),
    (204,"Hume", "hume", "Vic"),
    (205,"Latrobe - Gippsland", "latrobe_gippsland", "Vic"),
    (206,"Melbourne - Inner", "inner_melbourne", "Vic"),
    (207,"Melbourne - Inner East", "inner_east_melbourne", "Vic"),
    (208,"Melbourne - Inner South", "inner_south_melbourne", "Vic"),
    (209,"Melbourne - North East", "ne_melbourne", "Vic"),
    (210,"Melbourne - North West", "nw_melbourne", "Vic"),
    (211,"Melbourne - Outer East", "outer_east_melbourne", "Vic"),
    (212,"Melbourne - South East", "se_melbourne", "Vic"),
    (213,"Melbourne - West", "west_melbourne", "Vic"),
    (214,"Mornington Peninsula", "mornington", "Vic"),
    (215,"North West", "nw_victoria", "Vic"),
    (216,"Shepparton", "shepparton", "Vic"),
    (217,"Warrnambool and South West", "warnambool", "Vic"),
    (301,"Brisbane - East", "east_brisbane", "Qld"),
    (302,"Brisbane - North", "north_brisbane", "Qld"),
    (303,"Brisbane - South", "south_brisbane", "Qld"),
    (304,"Brisbane - West", "west_brisbane", "Qld"),
    (305,"Brisbane Inner City", "inner_brisbane", "Qld"),
    (306,"Cairns", "cairns", "Qld"),
    (307,"Darling Downs - Maranoa", "darling_downs", "Qld"),
    (308,"Fitzroy", "fitzroy", "Qld"),
    (309,"Gold Coast", "gold_coast", "Qld"),
    (310,"Ipswich", "ipswich", "Qld"),
    (311,"Logan - Beaudesert", "logan_beaudesert", "Qld"),
    (312,"Mackay", "mackay", "Qld"),
    (313,"Moreton Bay - North", "north_moreton_bay", "Qld"),
    (314,"Moreton Bay - South", "south_moreton_bay", "Qld"),
    (315,"Queensland - Outback", "outback_queensland", "Qld"),
    (316,"Sunshine Coast", "sunshine_coast", "Qld"),
    (317,"Toowoomba", "toowoomba", "Qld"),
    (318,"Townsville", "townsville", "Qld"),
    (319,"Wide Bay", "wide_bay", "Qld"),
    (401,"Adelaide - Central and Hills", "central_adelaide", "SA"),
    (402,"Adelaide - North", "north_adelaid", "SA"),
    (403,"Adelaide - South", "south_adelaid", "SA"),
    (404,"Adelaide - West", "west_adelaid", "SA"),
    (405,"Barossa - Yorke - Mid North", "barossa", "SA"),
    (406,"South Australia - Outback", "outback_sa", "SA"),
    (407,"South Australia - South East", "se_sa", "SA"),
    (501,"Bunbury", "bunbury", "WA"),
    (502,"Mandurah", "mandurah", "WA"),
    (503,"Perth - Inner", "inner_perth", "WA"),
    (504,"Perth - North East", "ne_perth", "WA"),
    (505,"Perth - North West", "nw_perth", "WA"),
    (506,"Perth - South East", "se_perth", "WA"),
    (507,"Perth - South West", "sw_perth", "WA"),
    (508,"Western Australia - Outback", "outback_wa", "WA"),
    (509,"Western Australia - Wheat Belt", "wheat_belt", "WA"),
    (601,"Hobart", "hobart", "Tas"),
    (602,"Launceston and North East", "launceston", "Tas"),
    (603,"South East", "se_tasmania", "Tas"),
    (604,"West and North West", "west_tasmania", "Tas"),
    (701,"Darwin", "darwin", "NT"),
    (702,"Northern Territory - Outback", "outback_nt", "NT"),
    (801,"Australian Capital Territory", "act", "ACT"),
]

decl_exceptions = {
        "obesity": [105, 315, 406, 508, 702],
}
        
parent = WidgetView.objects.get(label="australia")
vt = ViewType.objects.get(name="SA4 View")
p = Parametisation.objects.get(url="param_sa4")

for sa4 in sa4s:
    sa4_code = sa4[0]
    sa4_name = sa4[1]
    sa4_label = sa4[2]
    sa4_state = sa4[3]
    try:
        wv = WidgetView.objects.get(parent=parent, label=sa4_label)
        print "%s already exists" % sa4_label
    except WidgetView.DoesNotExist:
        print "Creating %s" % sa4_label
        wv = WidgetView(name=sa4_name, label=sa4_label, parent=parent, view_type=vt,
                sort_order=sa4_code)
    wv.save()
    if "sa4_code" not in wv.properties():
        cprop = ViewProperty(view=wv, key="sa4_code", property_type=ViewProperty.INT_PROPERTY, intval=sa4_code)
        cprop.save()
    if "sa4_name" not in wv.properties():
        nprop = ViewProperty(view=wv, key="sa4_name", property_type=ViewProperty.STR_PROPERTY, strval=sa4_name)
        nprop.save()
    if "state" not in wv.properties():
        sprop = ViewProperty(view=wv, key="state", property_type=ViewProperty.STR_PROPERTY, strval=sa4_state)
        sprop.save()
    props = wv.properties()
    if props["sa4_code"] != sa4_code or props["sa4_name"] != sa4_name or props["state"] != sa4_state:
        print "SA4 code %s property mismatch: %s" % (sa4_code, repr(props))
    for wd in WidgetDefinition.objects.filter(parametisation=p):
        exclude = sa4_code in decl_exceptions.get(wd.url(), [])
        try:
            decl = ViewWidgetDeclaration.objects.get(definition=wd, view=wv)
            if exclude:
                print "Deleting excluded view %s from %s" % (wv.label, wd.label)
                decl.delete()
        except ViewWidgetDeclaration.DoesNotExist:
            if not exclude:
                print "Adding view %s to %s" % (wv.label, wd.label)
                decl = ViewWidgetDeclaration(definition=wd, view=wv, sort_order=wd.sort_order)
                decl.save()

p.update()
