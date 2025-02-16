import chromadb
from chromadb.config import Settings

from core.config import settings


class ChromaClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = chromadb.Client(
                Settings(
                    persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                    is_persistent=True,
                )
            )
        return cls._instance
