from abc import abstractmethod, ABC
from typing import Optional


class Storage(ABC):

    @abstractmethod
    def save(
        self,
        local_file_path: str,
        target_path: str,
        content_type: Optional[str] = None,
    ) -> None:
        pass
