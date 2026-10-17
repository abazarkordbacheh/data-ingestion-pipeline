# ------------------------ Modules ------------------------
# Libraries =>
from abc import ABC, abstractmethod


# ------------------------ Class Base Connection ------------------------
class BaseConnection(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    def disconnect(self):
        pass
