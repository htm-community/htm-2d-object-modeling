


class TwoDimensionalEnvironment:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._features = [[None] * height] * width


    def size(self):
        return self._width * self._height


    def set_feature(self, x, y, f):
        self._features[x][y] = f


    def get_feature(self, x, y):
        return self._features[x][y]