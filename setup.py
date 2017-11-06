from distutils.core import setup

setup(
  name = 'goldencheetahlib',
  packages = ['goldencheetahlib'], # this must be the same as the name above
  version = '0.5.0',
  description = 'Python library that provides access to the GoldenCheeetah REST API',
  author = 'Aart Goossens',
  author_email = 'aart@goossens.me',
  url = 'https://github.com/AartGoossens/goldencheetahlib',
  download_url = 'https://github.com/AartGoossens/goldencheetahlib/tarball/0.4.0',
  keywords = ['workout', 'goldencheetah', 'cycling'],
  classifiers = [],
  install_requires=[
    'pandas>=0.18.1,<0.19',
    'requests>=2.10.0,<3',
    'matplotlib>=1.5.1,<2'
  ]
)
