import unittest

from htm2d.environment import TwoDimensionalEnvironment


class EnvironmentTests(unittest.TestCase):
	def test_load_features(self):
		env = TwoDimensionalEnvironment(28, 28)
		env.load_object(
			(
				"---\n"
				"name: Object A\n"
				"width: 20\n"
				"height: 20\n"
				"features:\n"
				"  - { x: 3, y: 3, data: A }\n"
				"  - { x: 4, y: 3, data: A }\n"
				"  - { x: 3, y: 4, data: B }\n"
			)
		)
		self.assertEqual(env.get_feature(3, 3), "A")
		self.assertEqual(env.get_feature(4, 3), "A")
		self.assertEqual(env.get_feature(3, 4), "B")

	def test_bigObject(self):
		env = TwoDimensionalEnvironment(5, 5)
		
		
		self.assertRaises(RuntimeError, env.load_object,(#object is bigger than environment
			(
				"---\n"
				"name: Object A\n"
				"width: 20\n"
				"height: 20\n"
				"features:\n"
				"  - { x: 3, y: 3, data: A }\n"
				"  - { x: 4, y: 3, data: A }\n"
				"  - { x: 3, y: 4, data: B }\n"
			)
		))
		
		self.assertRaises(RuntimeError, env.load_object,(#object contains invalid feature
			(
				"---\n"
				"name: Object A\n"
				"width: 5\n"
				"height: 5\n"
				"features:\n"
				"  - { x: 3, y: 3, data: A }\n"
				"  - { x: 4, y: 3, data: A }\n"
				"  - { x: 99, y: 4, data: B }\n"
			)
		))
			

	def test_sizeMatchesInputDimensions(self):
		env = TwoDimensionalEnvironment(28, 28)
		self.assertEqual(env.size(), 784)

	def test_setOneFeature(self):
		env = TwoDimensionalEnvironment(1, 1)
		env.set_feature(0, 0, "foo")
		self.assertEqual(env.get_feature(0, 0), "foo")

	def test_setManyFeatures(self):
		env = TwoDimensionalEnvironment(1, 2)
		env.set_feature(0, 0, "foo")
		env.set_feature(0, 1, "bar")
		self.assertEqual(env.get_feature(0, 0), "foo")
		self.assertEqual(env.get_feature(0, 1), "bar")

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
		self.assertEqual(w * h, count)
