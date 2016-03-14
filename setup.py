from setuptools import setup

setup(name='dicetables',
      version='0.2',
      description='fun with dice',
      url='http://github.com/eric-s-s/dice-tables',
      author='Eric Shaw',
      author_email='shaweric01@gmail.com',
      license='MIT',
      packages=['dicetables', 'tests'],
      install_requires=[
        'matplotlib', 'kivy' 
      ],
      zip_safe=False)