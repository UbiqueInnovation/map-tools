import multiprocessing
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
            config=Config(max_pool_connections=multiprocessing.cpu_count()),
        )

    @property
    def meteo_swiss_test(self) -> Bucket:
        return self.meteo_swiss_client.Bucket("app-test-static-fra.meteoswiss-app.ch")

    @property
    def meteo_swiss_prod(self) -> Bucket:
        return self.meteo_swiss_client.Bucket("app-prod-static-fra.meteoswiss-app.ch")
