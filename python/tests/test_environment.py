import unittest

from htm2d.environment import TwoDimensionalEnvironment


class EnvironmentTests(unittest.TestCase):

    def test_sizeMatchesInputDimensions(self):
        env = TwoDimensionalEnvironment(28, 28)
        self.assertEqual(env.size(), 784)

    def test_setOneFeature(self):
        env = TwoDimensionalEnvironment(1, 1)
        env.set_feature(0, 0, 'foo')
        self.assertEqual(env.get_feature(0, 0), 'foo')

    def test_setManyFeatures(self):
        env = TwoDimensionalEnvironment(1, 2)
        env.set_feature(0, 0, 'foo')
        env.set_feature(0, 1, 'bar')
        self.assertEqual(env.get_feature(0, 0), 'foo')
        self.assertEqual(env.get_feature(0, 1), 'bar')

    def test_allFeaturesAreInitiallyNone(self):
        w = 5
        h = 10
        count = 0
        env = TwoDimensionalEnvironment(w, h)
        for x in range(w):
            for y in range(h):
                f = env.get_feature(x, y)
                self.assertIsNone(f)
                count += 1
        self.assertEqual(w*h, count)

