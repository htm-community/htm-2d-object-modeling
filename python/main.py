#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 05:01:50 2019

@author: osboxes
"""

import os.path
import yaml
import htm2d.environment
import htm2d.agent
from htm2d.agent import Direction


objectFileName = 'a.yml'

#create environment and the agent
env = htm2d.environment.TwoDimensionalEnvironment(20,20)
agent = htm2d.agent.Agent()


#load object from yml file
with open(os.path.dirname(__file__) + '/../objects/'+objectFileName, 'r') as stream:
    try:
        env.load_object(stream)
    except yaml.YAMLError as exc:
        print(exc)
        

#put agent in the environment
agent.set_env(env,3,4)
print(agent.get_feature(Direction.UP))

for i in range(20):
    agent.moveDir(Direction.RIGHT)
    print(agent.get_feature(Direction.UP))






