import logging
import os
from abc import ABC, abstractmethod
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Iterable

import requests
from alive_progress import alive_bar


class Source(ABC):

    @property
    @abstractmethod
    def local_path(self) -> str:
        pass

    @abstractmethod
    def get_urls(self) -> Iterable[str]:
        pass

    def fetch_tile(self, tile_url: str) -> bool:
        file_name = tile_url.split("/")[-1]
        path = f'data/{self.local_path}/{file_name}'

        if os.path.exists(path):
            return False  # No need to download the fle again

        response = requests.get(tile_url, stream=True)
        if response.status_code != 200:
            raise IOError(f"Could not fetch {tile_url}")

        with open(path, 'wb') as f:
            for chunk in response:
                f.write(chunk)

        logging.debug(f"Saved {tile_url} to {path}")
        return True

    def download_tiles(self) -> None:
        os.makedirs(f'data/{self.local_path}/', exist_ok=True)

        urls = list(self.get_urls())

        thread_pool = ThreadPool(cpu_count())

        total_count = len(urls)
        downloaded_count = 0

        with alive_bar(total_count, title="Downloading tiles") as progress_bar:
            for downloaded in thread_pool.imap_unordered(self.fetch_tile, urls):
                progress_bar()
                if downloaded:
                    downloaded_count += 1

        logging.info(f"Downloaded {downloaded_count}, skipped {total_count - downloaded_count} tiles.")
