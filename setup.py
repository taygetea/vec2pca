from setuptools import setup, find_packages
from setuptools.command.install import install
import sys

class CustomInstall(install):
    def run(self):
        install.run(self)
        import nltk.downloader
        nltk.downloader.download("punkt")


if sys.version_info[0] <= 2:
    raise Exception('Needs Python 3')
setup(
    name = "w2v2c",
    version = "0.1",
    packages = find_packages(),
    scripts = ['word2vec.py', 'w2v2c.py'],
    install_requires = ['pandas', 'numpy', 'plac', 'nltk', 'BeautifulSoup', 'gensim', 'sklearn'],
    cmdclass={
        'install': CustomInstall,
    },
    

)
