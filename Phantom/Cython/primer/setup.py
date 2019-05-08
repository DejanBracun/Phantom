from setuptools import setup, Extension


setup(
    # ...
    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        'setuptools>=18.0',
        'cython',
    ],
    ext_modules=[
        Extension(
            'example_cython',
            sources=['example_cython.pyx'],
        ),
    ],
)