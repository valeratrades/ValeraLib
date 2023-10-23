from setuptools import setup, find_packages
# rm -rf dist build && python setup.py sdist bdist_wheel

setup(
    name="ValeraLib",
    version="1.0.0",
    description="The library goes brrrrrr",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Valera",
    author_email="v79166789533@gmail.com",
    url="https://github.com/Valera6/ValeraLib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
    "numpy>=1.24.3,<2.0.0",
    "pandas>=1.5.3,<2.0.0",
    "playsound>=1.2.2,<2.0.0",
    "plotly>=5.14.1,<6.0.0",
    "telebot",
    "requests>=2.31.0,<3.0.0"
	],
    python_requires='>=3.6',
    keywords="The greatest package to ever exist",
    include_package_data=True,
)
