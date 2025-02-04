import os

import boto3 as boto3
from botocore.config import Config
from dotenv import load_dotenv
from mypy_boto3_s3.service_resource import Bucket


class R2Client:
    def __init__(self) -> None:
        load_dotenv()  # take environment variables from .env.

        self.client = boto3.resource(
            service_name="s3",
            region_name="auto",
            endpoint_url=f'https://{os.environ["R2_ACCOUNT_ID"]}.r2.cloudflarestorage.com',
            aws_access_key_id=os.environ["R2_ACCESS_KEY"],
            aws_secret_access_key=os.environ["R2_SECRET_KEY"],
            config=Config(max_pool_connections=64),
        )

    @property
    def maps_dev(self) -> Bucket:
        return self.client.Bucket("maps-dev")

    @property
    def maps_prod(self) -> Bucket:
        return self.client.Bucket("maps-prod")

    @property
    def ubmeteo_app_dev(self) -> Bucket:
        return self.client.Bucket("ubmeteo-app-dev")

    @property
    def ubmeteo_app_prod(self) -> Bucket:
        return self.client.Bucket("ubmeteo-app-prod")

    @property
    def post_playground_dev(self) -> Bucket:
        return self.client.Bucket("post-playground-dev")

    @property
    def post_playground_int(self) -> Bucket:
        return self.client.Bucket("post-playground-int")

    @property
    def post_playground_prod(self) -> Bucket:
        return self.client.Bucket("post-playground-prod")
