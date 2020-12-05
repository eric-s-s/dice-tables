from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='dicetables',
      version='4.0.2',
      description='get all combinations for any set of dice',
      long_description=readme(),
      keywords='dice, die, statistics, table, probability, combinations',
      url='http://github.com/eric-s-s/dice-tables',
      author='Eric Shaw',
      author_email='shaweric01@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          "Operating System :: OS Independent",
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Games/Entertainment :: Role-Playing',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ],
      packages=find_packages(exclude=['tests', 'time_trials', 'docs']),
      install_requires=[],
      include_package_data=True,
      zip_safe=False)
