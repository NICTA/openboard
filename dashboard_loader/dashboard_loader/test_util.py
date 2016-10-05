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

from django.core.management import call_command
from django.test import TransactionTestCase

class DashboardTransactionTestCase(TransactionTestCase):
    imports = []
    widget_data = []
    
    def _pre_setup(self):
        super(DashboardTransactionTestCase, self)._pre_setup()
        try:
            self._imports_setup()
            self._widget_data_setup()
        except Exception:
            if self.available_apps is not None:
                apps.unset_available_apps()
                setting_changed.send(sender=settings._wrapped.__class__,
                                     setting='INSTALLED_APPS',
                                     value=settings.INSTALLED_APPS,
                                     enter=False)
            raise

    def _imports_setup(self):
        # N.B. Doesn't handle multiple databases etc - see
        #   django.test.TransactionTestCase._fixture_setup()
        if self.imports:
            call_command('import_data', *self.imports,
                        **{'verbosity': 0})

    def _widget_data_setup(self):
        # N.B. Doesn't handle multiple databases etc - see
        #   django.test.TransactionTestCase._fixture_setup()
        if self.widget_data:
            call_command('import_widget_data', *self.widget_data,
                        **{'verbosity': 0})

def json_equal(a, b, w, trace=[], ignore_keys=[]):
    if type(a) != type(b):
        raise Exception("Type mismatch:", w, type(a), type(b), trace)
    elif type(a) == list:
        if len(a) != len(b):
            raise Exception("Length mismatch:", w, len(a), len(b), trace)
        for i in range(len(a)):
            if not json_equal(a[i], b[i], w, trace + [i], ignore_keys):
                raise Exception("element mismatch:", w, a[i], b[i], trace, i)
        return True
    elif type(b) == dict:
        if len(a) != len(b):
            raise Exception("Length mismatch:", w, len(a), len(b), a.keys(), b.keys(), trace)
        for key in a.keys():
            if key in ignore_keys:
                pass
            elif not json_equal(a[key], b[key], w, trace + [key], ignore_keys):
                raise Exception("element mismatch:", w, a[key], b[key], trace, key)
        return True
    else:
        return a == b

