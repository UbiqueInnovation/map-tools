import os

from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv


class AzureClient:
    def __init__(self) -> None:
        load_dotenv()  # take environment variables from .env.

        self.flesk_dev_client = BlobServiceClient.from_connection_string(
            conn_str=os.environ["FLESK_DEV_CONNECTION_STRING"],
        )

        self.flesk_prod_client = BlobServiceClient.from_connection_string(
            conn_str=os.environ["FLESK_PROD_CONNECTION_STRING"],
        )

    @property
    def flesk_dev(self) -> ContainerClient:
        return self.flesk_dev_client.get_container_client("maps")

    @property
    def flesk_prod(self) -> ContainerClient:
        return self.flesk_prod_client.get_container_client("maps")
