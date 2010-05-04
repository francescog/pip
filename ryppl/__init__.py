
_run_setup_py = """
__file__ = %r
from setuptools.command import egg_info
def replacement_run(self):
    self.mkpath(self.egg_info)
    installer = self.distribution.fetch_build_egg
    for ep in egg_info.iter_entry_points('egg_info.writers'):
        # require=False is the change we're making:
        writer = ep.load(require=False)
        if writer:
            writer(self, ep.name, egg_info.os.path.join(self.egg_info,ep.name))
    self.find_sources()
egg_info.egg_info.run = replacement_run

import ryppl
import os
ryppl.project_directory = os.path.dirname(__SETUP_PY__)
execfile(__file__)
"""
