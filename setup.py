from setuptools import setup

setup(name='dicetables',
      version='0.3.2',
      description='fun with dice',
      keywords='dice, die, statistics, table, probability, combinations',
      url='http://github.com/eric-s-s/dice-tables',
      author='Eric Shaw',
      author_email='shaweric01@gmail.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License', 
        'Programming Language :: Python :: 2.7',  
      ],
      packages=['dicetables', 'tests'],
      #install_requires=[
      #  'matplotlib', 'kivy', 'kivy-garden' 
      #],
      include_package_data=True,
      zip_safe=False)