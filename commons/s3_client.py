import os

import boto3 as boto3
from botocore.config import Config
from dotenv import load_dotenv
from mypy_boto3_s3.service_resource import Bucket


class S3Client:
    def __init__(self) -> None:
        load_dotenv()  # take environment variables from .env.

        self.meteo_swiss_client = boto3.resource(
            service_name="s3",
            region_name="eu-central-1",
            aws_access_key_id=os.environ["METEO_SWISS_ACCESS_KEY"],
            aws_secret_access_key=os.environ["METEO_SWISS_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

        self.dwd_test_client = boto3.resource(
            service_name="s3",
            region_name="eu-central-1",
            aws_access_key_id=os.environ["DWD_TEST_ACCESS_KEY"],
            aws_secret_access_key=os.environ["DWD_TEST_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

        self.dwd_prod_client = boto3.resource(
            service_name="s3",
            region_name="eu-central-1",
            aws_access_key_id=os.environ["DWD_PROD_ACCESS_KEY"],
            aws_secret_access_key=os.environ["DWD_PROD_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

        self.viadi_dev_client = boto3.resource(
            service_name="s3",
            region_name="eu-central-1",
            aws_access_key_id=os.environ["VIADI_DEV_ACCESS_KEY"],
            aws_secret_access_key=os.environ["VIADI_DEV_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

        self.viadi_prod_client = boto3.resource(
            service_name="s3",
            region_name="eu-central-1",
            aws_access_key_id=os.environ["VIADI_PROD_ACCESS_KEY"],
            aws_secret_access_key=os.environ["VIADI_PROD_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

    @property
    def meteo_swiss_test(self) -> Bucket:
        return self.meteo_swiss_client.Bucket("app-test-static-fra.meteoswiss-app.ch")

    @property
    def meteo_swiss_prod(self) -> Bucket:
        return self.meteo_swiss_client.Bucket("app-prod-static-fra.meteoswiss-app.ch")

    @property
    def dwd_test(self) -> Bucket:
        return self.dwd_test_client.Bucket("app-dev-static.warnwetter.de")

    @property
    def dwd_prod(self) -> Bucket:
        return self.dwd_prod_client.Bucket("app-prod-static.warnwetter.de")

    @property
    def viadi_dev(self) -> Bucket:
        return self.viadi_dev_client.Bucket("app-dev-static.viadi-zero.ch")

    @property
    def viadi_prod(self) -> Bucket:
        return self.viadi_prod_client.Bucket("app-prod-static.viadi-zero.ch")
