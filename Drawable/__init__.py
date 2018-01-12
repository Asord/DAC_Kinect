from abc import abstractmethod, ABCMeta

# classe abstraite pour les objets de type drawable (doivent contenir et redéfinire update() et draw()
class drawable(object, metaclass=ABCMeta):

    @abstractmethod
    def update(self, *args):
        pass

    @abstractmethod
    def draw(self, *args):
        pass
