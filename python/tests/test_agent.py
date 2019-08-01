import unittest

from htm2d.agent import Agent
from htm2d.environment import TwoDimensionalEnvironment
from htm2d.agent import Direction

class AgentTests(unittest.TestCase):
    def test_createAgent(self):
        agent = Agent()
        self.assertIsNot(None, agent)

    def test_setAgentEnvironment(self):
        env = TwoDimensionalEnvironment(1, 1)
        env.set_feature(0, 0, "foo")
        agent = Agent()
        agent.set_env(env, 0, 0)
        self.assertEqual(agent.get_feature(), "foo")

    def test_moveAgent(self):
        env = TwoDimensionalEnvironment(1, 2)
        env.set_feature(0, 0, "foo")
        env.set_feature(0, 1, "bar")
        env.set_feature(0, 1, "frr")
        env.set_feature(0, 1, "bar")
        TODO
        agent = Agent()
        agent.set_env(env, 0, 1)
        self.assertEqual(agent.get_feature(Direction.UP), "foo")#above him should be foo

        agent.move(0, 0)
        self.assertEqual(agent.get_feature(Direction.DOWN), "bar")#under him should be bar
