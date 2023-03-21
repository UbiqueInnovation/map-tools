from __future__ import annotations

import asyncio
import logging
import os.path
from asyncio import Semaphore, TaskGroup
from typing import Iterable

from alive_progress import alive_bar
from httpx import AsyncClient, Limits


class FileDownloader:

    def __init__(self, urls: Iterable[str], path: str, progress_bar) -> None:
        self.path = path
        self.urls = list(urls)
        self.progress_bar = progress_bar or (lambda: None)
        self.max_concurrent_requests = 50
        self.client = AsyncClient(
            http2=True,
            timeout=None,
            limits=Limits(max_keepalive_connections=self.max_concurrent_requests))
        self.semaphore = Semaphore(self.max_concurrent_requests)

    async def __aenter__(self) -> FileDownloader:
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def download_file(self, url: str):

        file_name = url.split("/")[-1]
        path = f'{self.path}/{file_name}'
        if os.path.exists(path):
            self.progress_bar()
            return

        # Semaphore limits number of concurrent requests, by allowing at most a
        # fixed number of concurrent tasks to enter the following section
        async with self.semaphore:
            with open(path, 'wb') as f:
                async with self.client.stream('GET', url) as response:
                    if response.status_code != 200:
                        raise IOError(f"Could not fetch {url}")

                    async for chunk in response.aiter_bytes():
                        f.write(chunk)

            logging.debug(f"Saved {url} to {path}")
            self.progress_bar()

    async def download(self) -> None:
        async with TaskGroup() as task_group:
            for path in self.urls:
                task_group.create_task(self.download_file(path))

    @staticmethod
    def download_all(urls: Iterable[str], path: str) -> None:
        asyncio.run(FileDownloader.download_all_async(urls, path))

    @staticmethod
    async def download_all_async(urls: Iterable[str], path: str) -> None:
        urls = list(urls)
        with alive_bar(len(urls)) as progress_bar:
            async with FileDownloader(urls, path, progress_bar) as downloader:
                await downloader.download()
