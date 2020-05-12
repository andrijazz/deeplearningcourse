import numpy as np

from base_agent import BaseAgent
from utils import argmax


class SarsaAgent(BaseAgent):
    def __init__(self, agent_settings=None):
        super().__init__(agent_settings)
        self.actions = agent_settings['actions']
        self.lambd = agent_settings['lambd']
        self.gamma = 1

        # eligibility trace
        self.E = np.zeros((11, 22, len(self.actions)))
        # state -> state value
        # self.Q = np.random.rand(11, 22, len(self.actions))
        self.Q = np.zeros((11, 22, len(self.actions)))
        # state, action -> number of times action a is selected from state
        self.N = np.zeros((11, 22, len(self.actions)))

        # total reward over a single episode
        self.G = 0
        # last visited state
        self.last_state = None
        # last action taken
        self.last_action = None
        # eps parameter
        self.n0 = 100.

    def start(self, state):
        """
        Starting the agent
        :return: Returns initial action
        """
        rand = np.random.uniform()
        eps = self.n0 / (self.n0 + (self.N[state[0], state[1], 0] + self.N[state[0], state[1], 1]))
        if rand > eps:    # be greedy
            q_hit = self.Q[state[0], state[1], 0]
            q_stick = self.Q[state[0], state[1], 1]
            action = argmax([q_hit, q_stick])
        else:   # explore by taking random action
            action = np.random.choice(len(self.actions))

        self.N[state[0], state[1], action] = self.N[state[0], state[1], action] + 1

        self.last_action = action
        self.last_state = state
        return self.actions[action]

    def step(self, state, reward):
        """
        Agent step.

        :param state:
        :param reward:
        :return: next action
        """
        rand = np.random.uniform()
        eps = self.n0 / (self.n0 + (self.N[state[0], state[1], 0] + self.N[state[0], state[1], 1]))
        if rand > eps:    # be greedy
            q_hit = self.Q[state[0], state[1], 0]
            q_stick = self.Q[state[0], state[1], 1]
            action = argmax([q_hit, q_stick])
        else:   # explore by taking random action
            action = np.random.choice(len(self.actions))

        self.N[state[0], state[1], action] = self.N[state[0], state[1], action] + 1

        # do updates
        delta = reward + self.gamma * self.Q[state[0], state[1], action] - self.Q[self.last_state[0], self.last_state[1], self.last_action]
        self.E[self.last_state[0], self.last_state[1], self.last_action] = self.E[self.last_state[0], self.last_state[1], self.last_action] + 1

        for i in range(self.N.shape[0]):
            for j in range(self.N.shape[1]):
                for k in range(self.N.shape[2]):
                    if self.N[i, j, k] > 0:
                        alpha_t = 1. / self.N[i, j, k]
                        self.Q[i, j, k] = self.Q[i, j, k] + alpha_t * delta * self.E[i, j, k]
                        self.E[i, j, k] = self.lambd * self.E[i, j, k]

        self.last_state = state
        self.last_action = action
        return self.actions[action]

    def end(self):
        """
        Cleans up the agent properties
        :return:
        """
        self.G = 0
        self.last_state = None
        self.last_action = None