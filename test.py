import unittest
from pathlib import Path

cases = unittest.defaultTestLoader.discover(
    Path(__file__).absolute().parent / 'wechat' / 'tests',
    pattern='test*.py'
)
unittest.TextTestRunner().run(cases)
