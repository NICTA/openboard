import decimal

from django.db.models import Model
from django.db.utils import IntegrityError
from django.apps import apps

from dashboard_api.management.exceptions import ImportExportException
from widget_def.parametisation import parametise_label

def call_or_get_attr(obj, name):
    a = getattr(obj, name)
    if callable(a):
        return a()
    else:
        return a

class JSON_ATTR(object):
    """Default handler.  Just use the attribute"""
    def __init__(self, attribute=None, parametise=False, solo=False, default=None, importer=None):
        self.attribute = attribute
        self.parametise = parametise
        self.solo = solo
        self.importer = importer
        self.default = default
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.attribute:
            export[key] = call_or_get_attr(obj, self.attribute)
        else:
            export[key] = call_or_get_attr(obj, key)
        if self.parametise and recurse_func != "export":
            if parametisation is None and view is not None:
                # TODO
                pass
            export[key] = parametise_label(parametisation, view, export[key])
        if self.solo:
            env["single_export_field"] = key
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if self.solo:
            val = js
        else:
            val = js.get(key, self.default)
        if self.importer:
            val = self.importer(val)   
        if self.attribute:
            cons_args[self.attribute] = val
        else:
            cons_args[key] = val
    def recurse_import(self, js, obj, key, imp_kwargs, env, do_not_delete=False):
        pass

class JSON_PASSDOWN(JSON_ATTR):
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.attribute:
            val = call_or_get_attr(obj, self.attribute)
        else:
            val = call_or_get_attr(obj, key)
        val = getattr(val, recurse_func)(parametisation=parametisation, view=view)
        export[key] = val
        if self.solo:
            env["single_export_field"] = key
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class JSON_STRINGIFY_ATTR(JSON_ATTR):
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.attribute:
            export[key] = unicode(getattr(obj, self.attribute))
        else:
            export[key] = unicode(getattr(obj, key))
        return

class JSON_CAT_LOOKUP(JSON_ATTR):
    def __init__(self, lookup_fields, imp_lookup, attribute=None):
        super(JSON_CAT_LOOKUP, self).__init__(attribute=attribute)
        self.fields=lookup_fields
        self.imp_lookup=imp_lookup
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        o = obj
        for fld in self.fields:
            o = getattr(o, fld)
            if callable(o):
                o = o()
        export[key] = o
        return 
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if self.attribute:
            cons_args[self.attribute] = self.imp_lookup(js, key, imp_kwargs)
        else:
            cons_args[key] = self.imp_lookup(js, key, imp_kwargs)

class JSON_NUM_ATTR(JSON_ATTR):
    def __init__(self, precision, allow_int=True, attribute=None):
        self.precision = precision
        super(JSON_NUM_ATTR, self).__init__(attribute=attribute)
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.attribute:
            attrval = getattr(obj, self.attribute)
        else:
            attrval = getattr(obj, key)
        if attrval is None:
            export[key] = None
        elif allow_int and attrval == attrval.to_integral_value():
            export[key] = int(attrval)
        else:
            export[key] = float(attrval)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if js[key] is None:
            val = None
        else:
            val = decimal.Decimal(("%%.%df" % self.precision) % js[key]) 
        if self.attribute:
            cons_args[self.attribute] = val
        else:
            cons_args[key] = val

class JSON_OPT_ATTR(JSON_ATTR):
    def __init__(self, decider=None, attribute=None, parametise=False):
        super(JSON_OPT_ATTR, self).__init__(attribute=attribute, parametise=parametise)
        self.decider = decider
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.decider:
            do_it = call_or_get_attr(obj, self.decider)
        else:
            do_it = call_or_get_attr(obj, key)
        if do_it:
            super(JSON_OPT_ATTR, self).handle_export(obj, export, key, env, recurse_func, 
                            parametisation=parametisation, view=view)
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        if key in js:
            super(JSON_OPT_ATTR,self).handle_import(js, cons_args, key, imp_kwargs, env)

class JSON_IMPLIED(JSON_ATTR):
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]

class JSON_INHERITED(JSON_ATTR):
    def __init__(self, related_name):
        super(JSON_INHERITED, self).__init__()
        self.related = related_name
    def handle_export(self, *args, **kwargs):
        pass
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        cons_args[key] = imp_kwargs[key]
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        getattr(imp_kwargs[key], self.related).add(obj, bulk=False)

class JSON_COMPLEX_LOOKUP_WRAPPER(JSON_ATTR):
    def __init__(self, attribute, null, exporter, 
                    model, app, importer_kwargs, 
                    warning_on_importer_fail, name_key_for_warning):
        self.attribute = attribute
        self.null = null
        self.model = model
        self.app = app
        self.exporter = exporter
        self.importer_kwargs = importer_kwargs
        self.warning_on_importer_fail = warning_on_importer_fail
        self.name_key_for_warning = name_key_for_warning
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        export[key] = self.exporter(getattr(obj,self.attribute))
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        mdl = apps.get_app_config(self.app).get_model(self.model)
        if self.null and js[key] is None:
            lookup = None
        else:
            kwargs = self.importer_kwargs(js[key])
            try:
                lookup = mdl.objects.get(**kwargs)
            except mdl.DoesNotExist:
                print self.warning_on_importer_fail % js[self.name_key_for_warning]
                lookup = None
        cons_args[self.attribute] = lookup

class JSON_SIMPLE_LOOKUP_WRAPPER(JSON_ATTR):
    def __init__(self, attribute, null, exporters, 
                    model, app, importer_kwargs, 
                    warning_on_importer_fail=None, name_key_for_warning=None):
        self.attribute = attribute
        self.null = null
        self.model = model
        self.app = app
        self.exporters = exporters
        self.importer_kwargs = importer_kwargs
        self.warning_on_importer_fail = warning_on_importer_fail
        self.name_key_for_warning = name_key_for_warning
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        for k, exporter in zip(key, self.exporters):
            export[k] = exporter(getattr(obj,self.attribute))
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        mdl = apps.get_app_config(self.app).get_model(self.model)
        kwargs = self.importer_kwargs(js)
        try:
            lookup = mdl.objects.get(**kwargs)
        except mdl.DoesNotExist:
            if not self.null and self.warning_on_importer_fail:
                print self.warning_on_importer_fail % js[self.name_key_for_warning]
                lookup = None
            elif not self.null:
                raise ImportExportException("%s not found" % self.attribute)
            else:
                lookup = None
        cons_args[self.attribute] = lookup

class JSON_GEO_COORD(JSON_ATTR):
    def __init__(self, attribute, view_override_attribute=None, view_replacement_attribute=None):
        super(JSON_GEO_COORD, self).__init__(attribute=attribute)
        self.view_override_attr = view_override_attribute
        self.view_replacement_attr = view_replacement_attribute
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        keyx, keyy = key
        if self.view_override_attr and getattr(obj, self.view_override_attr) and view and getattr(view, self.view_replacement_attr):
            repl_win = getattr(view, self.view_replacement_attr)
            export[keyx] = repl_win.x
            export[keyy] = repl_win.y
        else:
            export[keyx] = getattr(obj, self.attribute).x 
            export[keyy] = getattr(obj, self.attribute).y 
        return
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        keyx, keyy = key
        from django.contrib.gis.geos import Point
        cons_args[self.attribute] = Point(js[keyx], js[keyy])

class JSON_RECURSEDOWN(JSON_ATTR):
    def __init__(self, model, related_name, related_attr, sub_attr_key, sub_exp_key=None, app=None, merge=True, suppress_if_empty=False, suppress_decider=None):
        super(JSON_RECURSEDOWN, self).__init__()
        self.related = related_name
        self.related_attr = related_attr
        self.app = app
        self.model = model
        self.suppress_if_empty = suppress_if_empty
        self.suppress_decider = suppress_decider
        self.merge = merge
        self.sub_attr_key = sub_attr_key
        if sub_exp_key:
            self.sub_exp_key = sub_exp_key
        else:
            self.sub_exp_key = sub_attr_key
    def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        if self.suppress_if_empty and getattr(obj, self.related).count() == 0:
            pass
        elif self.suppress_decider and call_or_get_attr(obj, self.suppress_decider):
            pass
        elif key:
            export[key] = [ o.export() for o in getattr(obj, self.related).all() ] 
        else: 
            for o in getattr(obj, self.related).all():
                if view:
                    export.append(getattr(o, recurse_func)(parametisation=parametisation, view=view))
                else:
                    export.append(getattr(o, recurse_func)())
    def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass
    def recurse_import(self,js, obj, key, imp_kwargs, env, do_not_delete=False):
        if self.app:
            model = apps.get_app_config(self.app).get_model(self.model)
        else:
            model = self.model
        base_kwargs = {}
        base_kwargs[self.related_attr] = obj
        if key is None:
            _js = js
        elif self.suppress_if_empty or self.suppress_decider:
            _js = js.get(key, [])
        else:
            _js = js[key]
        keys_in_import=[]
        if self.merge:
            for js_elem in _js:
                keys_in_import.append(js_elem[self.sub_exp_key])
            for elem in getattr(obj,self.related).all():
                elem_key = getattr(elem, self.sub_attr_key)
                if elem_key not in keys_in_import and not do_not_delete:
                    elem.delete()
        elif not do_not_delete:
            getattr(obj, self.related).all().delete()
        for i in range(len(_js)):
            kwargs = base_kwargs.copy()
            kwargs["merge"] = do_not_delete
            if "sort_order" not in kwargs:
                kwargs["sort_order"] = (i + 1)*100
            kwargs["js"] = _js[i]
            saved = False
            while not saved:
                try:
                    model.import_data(**kwargs)
                    saved = True
                except IntegrityError:
                    kwargs["sort_order"] += 1

class JSON_RECURSEDICT(JSON_ATTR):
   def __init__(self, related, key_attr, value_attr): 
       self.related = related
       self.key_attr = key_attr
       self.value_attr = value_attr
   def handle_export(self, obj, export, key, env, recurse_func="export", parametisation=None, view=None):
        exp = {}
        for o in getattr(obj, self.related).all():
            exp[getattr(o, self.key_attr)] = getattr(o, self.value_attr)
        export[key] = exp
        return
   def handle_import(self, js, cons_args, key, imp_kwargs, env):
        pass

class WidgetDefJsonMixin(object):
    export_def = {
    }
    export_lookup = {}
    api_state_def = {
    }
    def export(self):
        if None in self.export_def:
            exp = []
        else:
            exp = {}
        env = {
            "single_export_field": False
        }
        for k, v in self.export_def.items():
            v.handle_export(self, exp, k, env)
        if env["single_export_field"]:
            return exp[env["single_export_field"]]
        else:
            return exp
    def __getstate__(self, parametisation=None, view=None):
        if None in self.api_state_def:
            data = []
        else:
            data = {}
        env = {
            "single_export_field": False
        }
        for k, v in self.api_state_def.items():
            v.handle_export(self, data, k, env, recurse_func="__getstate__", parametisation=parametisation, view=view)
        if env["single_export_field"]:
            return data[env["single_export_field"]]
        else:
            return data
    @classmethod
    def import_data(cls, js, **kwargs):
        cons_args = kwargs.copy()
        if "merge" in kwargs:
            merge = kwargs["merge"]
            del cons_args["merge"]
        else:
            merge = False
        env = { "save": True }
        for k, v in cls.export_def.items():
            v.handle_import(js, cons_args, k, kwargs, env)
        if cls.export_lookup:
            get_kwargs = {}
            for v in cls.export_lookup.values():
                get_kwargs[v] = cons_args[v]
            try:
                obj = cls.objects.get(**get_kwargs)
                for k,v in cons_args.items():
                    if k not in cls.export_lookup:
                        setattr(obj, k, v)
            except cls.DoesNotExist:
                obj = cls(**cons_args)
        else:
            obj = cls(**cons_args)
        if env["save"]:
            obj.save()
        for k, v in cls.export_def.items():
            v.recurse_import(js, obj, k, kwargs, env, do_not_delete=merge)
        return obj

