from django.core.management import call_command
from django.test import TransactionTestCase

class DashboardTransactionTestCase(TransactionTestCase):
    imports = []
    
    def _pre_setup(self):
        super(DashboardTransactionTestCase, self)._pre_setup()
        try:
            self._imports_setup()
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

