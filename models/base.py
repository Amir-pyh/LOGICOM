from abc import ABC, abstractmethod


class ModelBackbone(ABC):
    @abstractmethod
    def run(self):
        r"""run the query on model"""
        pass
