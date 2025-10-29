from setuptools import find_packages, setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="nc-api",
    version="0.2.2",
    author="ODNA_SHESTA",
    author_email="playcola2003@gmail.com",
    url="https://github.com/odnashestaia/nc-api-python",
    license="MIT",
    description="Nextcloud WebDAV client (files, directories, paths, users)",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
    ],
    include_package_data=True,
    project_urls={"GitHub": "https://github.com/odnashestaia/nc-api-python"},
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
