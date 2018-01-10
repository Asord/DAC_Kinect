from abc import abstractmethod, ABCMeta

# abstract class drawable for drawable pygame objects
class drawable(object, metaclass=ABCMeta):

    @abstractmethod
    def update(self, *args):
        pass

    @abstractmethod
    def draw(self, *args):
        pass
