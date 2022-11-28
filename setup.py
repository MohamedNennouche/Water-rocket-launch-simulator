from setuptools import setup, find_packages


setup(
      name='WaterRocket',
      version='0.1.5',
      license='MIT',
      author="Mohamed Nennouche",
      author_email='moohaameed.nennouche@gmail.com',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      url='https://github.com/MohamedNennouche/Water-rocket-launch-simulator',
      keywords='water rocket simulation',
      install_requires=[
            'matplotlib',
            'numpy',
            'pandas',
            'reportlab',
            'seaborn',
            'tabulate'
      ],
      long_description="""WaterRocket is a Python module for simulating the firing of a water rocket, allowing to generate graphs of the evolution during the flight as well as a PDF report of this flight""",
      long_description_content_type='text/markdown',

)