


class Agent():

    def set_env(self, env, x, y):
        self._env = env
        self._f = env.get_feature(x, y)

    def get_feature(self):
        return self._f

    def move(self, x, y):
        self._f = self._env.get_feature(x, y)