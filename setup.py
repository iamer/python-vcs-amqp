from distutils.core import setup
from setuptools import find_packages

def debpkgver(changelog="debian/changelog"):
    """read version from the debian/changelog file"""
    return open(changelog).readline().split()[1][1:-1]

setup(
    name="vcsamqp",
    version=debpkgver(),
    url='https://github.com/iamer/python-vcs-amqp',
    author='BIFH & OBS teams',
    author_email='bifh-team@nokia.com',
    packages=find_packages(exclude=['ez_setup']),
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
