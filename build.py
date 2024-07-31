import os

from setuptools import Extension
from setuptools.command.build_ext import build_ext


extra_compile_args=["-Wall"]
if os.name == 'nt':
    extra_compile_args.append("/Ox")
else:
    extra_compile_args.append("-O3")


extensions = [
    Extension(
        'ipset_c_ext',
        ['src/ipset_c.c', 'src/net_range_container.c', 'src/net_range.c'],
        extra_compile_args=extra_compile_args,
        py_limited_api=False,
    ),
]


class BuildFailed(Exception):
    pass


class ExtBuilder(build_ext):
    def run(self):
        build_ext.run(self)

    def build_extension(self, ext):
        build_ext.build_extension(self, ext)


def build(setup_kwargs):
    setup_kwargs.update({"ext_modules": extensions, "cmdclass": {"build_ext": ExtBuilder}})
