from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools.errors import CCompilerError, ExecError, PlatformError


extensions = [
    Extension(
        'ipset_c_ext',
        ['src/ipset_c.c', 'src/net_range_container.c', 'src/net_range.c'],
        extra_compile_args=["-O3", "-Wall"],
        py_limited_api=True,
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
