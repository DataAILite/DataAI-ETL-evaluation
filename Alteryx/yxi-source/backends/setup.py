"""Build definition for the DataAI ETL Alteryx Python back end."""

from setuptools import find_packages, setup


setup(
    name="dataai-etl-alteryx",
    version="0.1.0.dev1",
    description="Alteryx adapter for customer-controlled DataAI Spark ETL libraries",
    platforms=["Windows"],
    author="Yanbor LLC",
    packages=find_packages(),
    package_data={"ayx_plugins": ["runtime/*.jar"]},
    include_package_data=True,
)
