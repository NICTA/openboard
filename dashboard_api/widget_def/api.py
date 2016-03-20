#   Copyright 2015,2016 NICTA
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.http import Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Min, Max

from widget_def.models import *
from widget_def.view_utils import *
from widget_data.models import GeoProperty

def api_get_top_level_views(user):
    if user.is_authenticated():
        # TODO View permissions
        views = WidgetView.objects.filter(parent__isnull=True)
    else:
        views = WidgetView.objects.filter(parent__isnull=True,requires_authentication=False)
    return [ v.desc() for v in views ]

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

def api_get_view(view):
    return view.__getstate__()

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
        elif len(menu) == 0:
            raise Http404("No map datasets defined for this view")
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

def api_get_terria_init(theme,location,frequency, shown=[]):
    init =  {
        "catalog": [{
                    "name": settings.TERRIA_TOP_LEVEL_MENU,
                    "type": "group",
                    "isOpen": "true",
                    "items": []
                   }],
        "homeCamera": location.geo_window.__getstate__(),
        "baseMapName": settings.TERRIA_BASE_MAP_NAME,
        "corsDomains": settings.TERRIA_CORS_DOMAINS,
    }
    for cat in Category.objects.all():
        cm = {
            "name" : cat.name,
            "type": "group",
            "isOpen": "true",
            "items" : [],
        }
        for sub in cat.subcategory_set.all():
            sm = {
                "name" : sub.name,
                "type": "group",
                "isOpen": "true",
                "items" : [],
            }
            decls = GeoDatasetDeclaration.objects.filter(theme=theme,
                                            location=location,
                                            frequency=frequency,
                                            dataset__subcategory=sub)
            for decl in decls:
                sm["items"].append(catalog_entry(decl.dataset, theme, location, frequency, shown))
            if len(sm["items"]) > 0:
                cm["items"].append(sm)
        cm_len = len(cm["items"])
        if cm_len > 0:
            if cm_len == 1:
                cm["items"] = cm["items"][0]["items"]
            init["catalog"][0]["items"].append(cm)
    if len(init["catalog"][0]["items"]) == 1:
        init["catalog"][0]["items"] = init["catalog"][0]["items"][0]["items"]
    elif len(init["catalog"][0]["items"]) == 0:
        raise Http404("No map datasets defined for this view")
    return init

def catalog_entry(ds, theme, location, frequency, shown=[]):
    use_csv = ds.terria_prefer_csv()
    entry = {
        "name": ds.label,
        "opacity": settings.TERRIA_LAYER_OPACITY,
    }
    if ds.url in shown:
        entry["isShown"] = True
    if ds.is_external():
        entry["url"] = ds.ext_url
        entry["type"] = ds.ext_type
        if ds.ext_extra:
            entry.update(entry)
        return entry 
    get_args = {
        "location": location.url,
        "theme": theme.url,
        "frequency": frequency.url,
        "headings": "label",
    }
    if use_csv:
        entry["type"] = "csv"
        get_args["format"] = "csv"
        try:
            dataprop = ds.geopropertydefinition_set.get(data_property=True)
            entry["tableStyle"] = { "dataVariable": dataprop.label }
            tab = ds.colour_table()
            if tab:
                entry["tableStyle"]["minDisplayValue"] = tab.min
                entry["tableStyle"]["maxDisplayValue"] = tab.max
                entry["tableStyle"]["colorMap"] = ds.colour_table().terria_map()
        except GeoPropertyDefinition.DoesNotExist:
            pass
    else:
        entry["type"] = "geojson"
        get_args["format"] = "json"
    base_url = reverse('get_map_data', args=(ds.url,))
    url = settings.TERRIA_API_BASE + base_url + "?" + "&".join([ "%s=%s" % (k,v) for (k,v) in get_args.items() ])
    entry["url"] = url
    return entry

