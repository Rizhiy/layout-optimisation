import codecs
import os

from setuptools import find_packages, setup

_module_name = "layout_optimisation"


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_requirements(rel_path):
    reqs = []
    for line in read(rel_path).splitlines():
        if line.startswith("#") or line.startswith("--"):
            continue
        if ".git" in line:
            package_name = line.split("/")[-1].split(".")[0]
            line = f"{package_name}@{line}"
        reqs.append(line.strip())
    return reqs


setup(
    name=_module_name,
    version=get_version(f"{_module_name}/__init__.py"),
    description="Keyboard Layout Optimisation",
    author="Artem Vasenin",
    author_email="vasart169@gmail.com",
    packages=find_packages(exclude=["tests*"]),
    install_requires=get_requirements(f"{_module_name}/requirements.txt"),
)
