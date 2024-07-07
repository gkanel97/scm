from abc import ABC, abstractmethod

class ViewInterface(ABC):
    def __init__(self, title):
        self.title = title
        # self.base_url = 'http://localhost:8000/api/'

    @abstractmethod
    def fetch_data(self):
        pass

    @abstractmethod
    def display_data(self, data):
        pass
