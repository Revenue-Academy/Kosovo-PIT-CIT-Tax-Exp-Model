import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'taxcalc/_version.py'
versioneer.versionfile_build = 'taxcalc/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'taxcalc-'  # dirname like 'taxcalc-1.2.0'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
        longdesc = f.read()

version = versioneer.get_version()
cmdclass = versioneer.get_cmdclass()

config = {
    'description': 'pitaxcalc-demo',
    'url': 'https://github.com/TPRU-demo/pitaxcalc-demo',
    'download_url': 'https://github.com/TPRU-demo/pitaxcalc-demo',
    'description': 'pitaxcalc-demo',
    'long_description': longdesc,
    'version': version,
    'cmdclass': cmdclass,
    'license': 'MIT',
    'packages': ['taxcalc'],
    'include_package_data': True,
    'name': 'taxcalc',
    'install_requires': ['numpy', 'pandas', 'numba', 'toolz'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    'tests_require': ['pytest']
}

setup(**config)
