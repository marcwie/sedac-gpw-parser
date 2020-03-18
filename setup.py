import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sedac_gpw_parser", # Replace with your own username
    version="0.1",
    author="Marc Wiedermann",
    author_email="marcwie@pik-potsdam.de",
    description="Framework to work with high-resolution population estimates from the Socioeconomic Data and Applications Center",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcwie/sedac-gpw-parser",
    packages=setuptools.find_packages(include=("sedac_gpw_parser",)),
    #classifiers=[
    #    "Programming Language :: Python :: 3",
    #    "License :: OSI Approved :: MIT License",
    #    "Operating System :: OS Independent",
    #],
    scripts=("bash_scripts/download-sedac-gpw-data.sh", ),
    python_requires='>=3',
)
