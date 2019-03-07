import unittest

from htm2d.agent import Agent
from htm2d.environment import TwoDimensionalEnvironment


class AgentTests(unittest.TestCase):

    def test_createAgent(self):
        agent = Agent()

    def test_setAgentEnvironment(self):
        env = TwoDimensionalEnvironment(1, 1)
        env.set_feature(0,0, 'foo')
        agent = Agent()
        agent.set_env(env, 0, 0)
        self.assertEqual(agent.get_feature(), 'foo')


    def test_moveAgent(self):
        env = TwoDimensionalEnvironment(1, 2)
        env.set_feature(0, 0, 'foo')
        env.set_feature(0, 1, 'bar')
        agent = Agent()
        agent.set_env(env, 0, 0)
        self.assertEqual(agent.get_feature(), 'foo')
        agent.move(0, 1)
        self.assertEqual(agent.get_feature(), 'bar')

