# Agent is entity with four sensors around him
from enum import Enum


class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class Agent:
    def set_env(self, env, x, y):
        self._env = env
        self._x = x
        self._y = y

    def get_feature(self, sensorLoc):
        if type(sensorLoc) != Direction:
            raise TypeError("Use enumeration Direction!")

        if sensorLoc == Direction.LEFT:
            f = self._env.get_feature(self._x - 1, self._y)
        elif sensorLoc == Direction.RIGHT:
            f = self._env.get_feature(self._x + 1, self._y)
        elif sensorLoc == Direction.UP:
            f = self._env.get_feature(self._x, self._y - 1)
        elif sensorLoc == Direction.DOWN:
            f = self._env.get_feature(self._x, self._y + 1)
        else:
            raise NotImplemented("Wrong SensorLoc!")
        return f

    def get_position(self):
        return [self._x, self._y]

    def move(self, x, y):
        if x < 0 or y < 0 or x >= self._env._width or y >= self._env._height:
            raise RuntimeError(
                "Can't move outside environment borders!Pos:" + str([x, y])
            )
        self._x = x
        self._y = y

    def moveDir(self, direction):
        x = self._x
        y = self._y
        if direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1
        elif direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        else:
            raise NotImplemented("Wrong direction!")

        self.move(x, y)
