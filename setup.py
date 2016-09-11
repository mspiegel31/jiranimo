from setuptools import find_packages, setup

setup(name='jiranimo',
      version='0.1',
      description='utils for getting data out of Jira',
      author='Mike Spiegel',
      author_email='mspiegel31@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'Click',
          'jira',
      ],
      entry_points='''
        [console_scripts]
        jiranimo=jiranimo.scripts.cli:cli
        ''',
      )
