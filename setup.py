from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='geonpy',
      version='0.0.1',
      description='Geonpy class',
      url='http://github.com/cwarecsiro/geonpy',
      author='Chris Ware',
      author_email='chris.ware@csiro.au',
      license='NA',
      packages=['geonpy'],
      #test_suite='nose.collector',
      #tests_require=['nose'],
      zip_safe=False,
      install_requires=[
          'rasterio', 'feather-format',
      ]
      #entry_points={
      #  'console_scripts': [
      #      'calc = climate_indicies.calc.__main__:main'
      #  ]
    #},
)