#   Copyright 2015 NICTA
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

from dashboard_loader.models import Loader, Uploader

from django.contrib.auth.models import Group
from django.utils.importlib import import_module

def register(app, refresh_rate=None):
    if refresh_rate is None:
        # uploader
        try:
            l = Uploader.objects.get(app=app)
            result = False
        except Uploader.DoesNotExist:
            l = Uploader(app=app)
            l.save()
            result = True
        p = l.permission()
        groups = get_uploader_groups(app)
        for grp in groups:
            try:
                g = Group.objects.get(name=grp)
            except Group.DoesNotExist:
                g = Group(name=grp)
                g.save()
            g.permissions.add(p)
        for grp in Group.objects.all():
            if grp.name not in groups:
                g.permissions.remove(p)
        return result
    else:
        # loader
        old_rate = None
        try:
            l = Loader.objects.get(app=app)
            if l.refresh_rate == refresh_rate:
                return l.refresh_rate
            old_rate = l.refresh_rate
        except Loader.DoesNotExist:
            l = Loader(app=app, suspended=True)
        l.refresh_rate = refresh_rate
        l.save()
        return old_rate

def get_uploader_groups(app):
    return import_module(app + ".uploader").groups
