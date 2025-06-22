from setuptools import setup

setup(
   name='djikstra_lib',
   version='1.0',
   description='about djikstra',
   license='MIT',
   author='Svetlana Rudova',
   author_email='rudovasvetlana570@gmail.com',
   url='https://github.com/rudessa/djikstra_lib',
   packages=['djikstra'],
   install_requires=[
       'itertools',
       'heapq'
   ], 
   extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
   },
   python_requires='>=3',
)