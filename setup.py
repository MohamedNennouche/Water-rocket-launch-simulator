from setuptools import setup, find_packages


setup(
    name='WaterRocket',
    version='0.1.0',
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

)