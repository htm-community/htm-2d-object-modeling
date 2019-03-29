
import yaml

class TwoDimensionalEnvironment:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._features = [[None] * height] * width

    def load_object(self, yaml_text):
        obj = yaml.load(yaml_text)
        for feature in obj.get("features"):
            x = feature.get("x")
            y = feature.get("y")
            data = feature.get("data")
            self._features[x][y] = data

    def size(self):
        return self._width * self._height


    def set_feature(self, x, y, f):
        self._features[x][y] = f


    def get_feature(self, x, y):
        return self._features[x][y]