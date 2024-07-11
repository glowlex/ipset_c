import os
from pathlib import Path

import pytest



@pytest.fixture(scope='session', autouse=True)
def compileIpset():
    _delCompiledFile()
    if 'compileForTests' in os.environ:
        from setuptools import setup
        from build import extensions
        setupDict = {
            "name": 'ipset_c',
            "version": "0.1.0.dev0",
            "ext_modules": extensions,
        }
        setupDict['script_args'] = ["build_ext", "--inplace"]
        setup(**setupDict)


def _delCompiledFile():
    for p in Path('.').glob('ipset_c_ext.pyd'):
        p.unlink()
    for p in  Path('.').glob('ipset_c_ext.*.so'):
        p.unlink()
