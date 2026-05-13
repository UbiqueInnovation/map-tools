from abc import abstractmethod, ABC


class Storage(ABC):

    @abstractmethod
    def save(self, local_file_path: str, target_path: str) -> None:
        pass
