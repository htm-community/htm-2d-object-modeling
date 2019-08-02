import unittest

from htm2d.agent import Agent
from htm2d.environment import TwoDimensionalEnvironment
from htm2d.agent import Direction

class AgentTests(unittest.TestCase):
    def test_createAgent(self):
        agent = Agent()
        self.assertIsNot(None, agent)

    def test_setAgentEnvironment(self):
        env = TwoDimensionalEnvironment(2, 2)
        env.set_feature(0, 0, "foo")
        agent = Agent()
        agent.set_env(env, 0, 1)
        self.assertEqual(agent.get_feature(Direction.UP), "foo")#above him should be foo

    def test_moveAgent(self):
        env = TwoDimensionalEnvironment(3, 3)
        env.set_feature(0, 0, "foo1")
        env.set_feature(0, 1, "foo2")
        env.set_feature(2, 1, "foo3")
        env.set_feature(1, 2, "foo4")
        
        agent = Agent()
        agent.set_env(env, 0, 1)
        self.assertEqual(agent.get_feature(Direction.UP), "foo1")
        agent.move(1, 1)
        self.assertEqual(agent.get_feature(Direction.LEFT), "foo2")
        self.assertEqual(agent.get_feature(Direction.RIGHT), "foo3")
        self.assertEqual(agent.get_feature(Direction.DOWN), "foo4")

    def test_checkBorders(self):
        env = TwoDimensionalEnvironment(2, 2)
        
        agent = Agent()
        agent.set_env(env, 0, 0)
        self.assertEqual(agent.get_feature(Direction.UP), None)
        self.assertEqual(agent.get_feature(Direction.LEFT), None)
        
        agent.move(1, 1)
        self.assertEqual(agent.get_feature(Direction.DOWN), None)
        self.assertEqual(agent.get_feature(Direction.RIGHT), None)
        
    def test_moveDirAgent(self):#ensure that moveDir() behaves in consistent with move()
        env = TwoDimensionalEnvironment(3, 3)
        
        agent1 = Agent()
        agent1.set_env(env, 0, 1)
        
        agent2 = Agent()
        agent2.set_env(env, 0, 1)
        
        self.assertEqual(agent1.get_position(),agent2.get_position())
        agent1.move(0,2)
        self.assertNotEqual(agent1.get_position(),agent2.get_position())
        agent2.moveDir(Direction.DOWN)
        self.assertEqual(agent1.get_position(),agent2.get_position())
        agent1.move(0,1)
        agent2.moveDir(Direction.UP)
        self.assertEqual(agent1.get_position(),agent2.get_position())
        agent1.move(1,1)
        agent2.moveDir(Direction.RIGHT)
        self.assertEqual(agent1.get_position(),agent2.get_position())
        agent1.move(0,1)
        agent2.moveDir(Direction.LEFT)
        self.assertEqual(agent1.get_position(),agent2.get_position())
        
        
        
        