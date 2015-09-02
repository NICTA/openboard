from widget_def.models import *

def api_get_themes(user):
    if user.is_authenticated():
        # TODO Theme based permissions
        themes = Theme.objects.all()
    else:
        themes = Theme.objects.filter(requires_authentication=False)
    return [ t.__getstate__() for t in themes ]

def api_get_locations():
    return [ l.__getstate__() for l in Location.objects.all() ]

def api_get_frequencies():
    return [ f.__getstate__() for f in Frequency.objects.filter(display_mode=True) ]

def api_get_icon_libraries():
    return { l.name : l.__getstate__() for l in IconLibrary.objects.all() }

def api_get_widgets(theme, location, frequency):
    widgets = WidgetDeclaration.objects.filter(theme=theme, 
                    location=location, 
                    frequency=frequency)
    return [ w.__getstate__() for w in widgets ]

def api_get_map_layers(theme, location, frequency, hierarchical=False):
    menu = []
    if hierarchical:
        for cat in Category.objects.all():
            cm = {
                "menu_label" : cat.name,
                "content" : [],
            }
            for sub in cat.subcategory_set.all():
                sm = {
                    "menu_label" : sub.name,
                    "content" : [],
                }
                decls = GeoDatasetDeclaration.objects.filter(theme=theme,
                                                location=location,
                                                frequency=frequency,
                                                dataset__subcategory=sub)
                for decl in decls:
                    sm["content"].append(decl.__getstate__())
                if len(sm["content"]) > 0:
                    cm["content"].append(sm)
            cm_len = len(cm["content"])
            if cm_len > 0:
                if cm_len == 1:
                    cm["content"] = cm["content"][0]["content"]
                menu.append(cm)
        if len(menu) == 1:
            menu = menu[0]["content"]
    else:
        decls = GeoDatasetDeclaration.objects.filter(theme=theme,
                                    location=location,
                                    frequency=frequency)
        for decl in decls:
            menu.append(decl.__getstate__())
    return {
        "window": location.geo_window.__getstate__(),
        "menu": menu,
    }

