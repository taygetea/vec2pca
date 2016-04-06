from setuptools import setup, find_packages
from setuptools.command.install import install
import sys

if sys.version_info[0] <= 2:
    raise Exception('Needs Python 3')
setup(
    name = "vec2pca",
    version = "0.1",
    packages = find_packages(),
    scripts = ['vec2pca.py'],
    install_requires = ['scipy', 'pandas', 'numpy', 'plac', 'nltk', 'BeautifulSoup', 'gensim', 'sklearn'],
)

