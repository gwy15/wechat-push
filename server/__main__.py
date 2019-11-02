

import os
import sys

__entry_point__ = None
if '__file__' in locals() and __file__ is not None:
  __entry_point__ = os.path.dirname(__file__)
elif '__loader__' in locals():
  from pkgutil import ImpLoader
  if hasattr(__loader__, 'archive'):
    __entry_point__ = __loader__.archive
  elif isinstance(__loader__, ImpLoader):
    __entry_point__ = os.path.dirname(__loader__.get_filename())

if __entry_point__ is None:
  sys.stderr.write('Could not launch python executable!\n')
  sys.exit(2)

sys.path[0] = os.path.abspath(sys.path[0])
sys.path.insert(0, os.path.abspath(os.path.join(__entry_point__, '.bootstrap')))

from pex.third_party import VendorImporter
VendorImporter.install(uninstallable=False,
                       prefix='_pex',
                       path_items=['pex'],
                       warning='Runtime pex API access through the `_pex` '
                               'package is deprecated and will be removed in pex 2.0.0. Please '
                               'switch to the `pex` package for runtime API access.')

from pex.pex_bootstrapper import bootstrap_pex
bootstrap_pex(__entry_point__)
