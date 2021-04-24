from setuptools import find_packages, setup


with open('requirements.txt') as f_required:
    required = f_required.read().splitlines()

setup(
    name='omdbweather',
    description='mini python app to run omdbweather',
    long_description='mini python app to run omdbweather',
    long_description_content_type='text/x-rst',
    author="reubinoff",
    author_email="reubinoff@gmail.com",
    version="1.0.0",
    python_requires='>=3.7, <3.9',
    packages=find_packages(exclude=[]),
    install_requires=required,
    exclude=["docs","tests", ".gitignore", "README.rst","DESCRIPTION.rst"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points = {
        'console_scripts': ['omdbweather = omdbweather.__main__:run_app'],
    }
)