import fab_guard
from fab_guard import fgcheck
import config as config
from tests import *


@fgcheck
def test_all_files(self):
    self.register_for_test(distr_age_schema.DistrAgeScheme, config.distr_age)
    # self.register_for_test(location_scheme.LocationsScheme, config.locations)
    # self.register_for_test(routes_scheme.RoutesScheme, config.routes)
    # self.register_for_test(closures_scheme.ClosuresScheme, config.closures)


print("Hello World")
fg = fab_guard.FabGuard(config.input_file_dir)
fg.verify()