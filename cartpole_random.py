##Mainly inspired from http://kvfrans.com/simple-algoritms-for-solving-cartpole/

import gym
import numpy as np

GAME = 'CartPole-v0'

def play_game():
    env = gym.make(str(GAME))
    total_reward = 0
    par = np.random.rand(4) * 2 - 1
    best_reward = 0

    def new_env(env,par):
        observation = env.reset()   #read in the parameters
        total_reward = 0
        for _ in range(200):
            env.render()
            action = 0 if np.matmul(par,observation) < 0 else 1
            observation, reward, done, info = env.step(action)
            print (observation, reward, done, info)
            total_reward += reward
            if done:
                break
        return total_reward

    for t in range(1000):
        total_reward = new_env(env,par)
        #print (observation, "\n", reward, "\n", info, total_reward, action)
        if total_reward > best_reward:
            best_reward = total_reward
            best_par = par
            if total_reward >= 200:
                print (best_par)
                print ("Episode finished after {} timesteps".format(t+1))
                break
        else:
            print ("No answer!")


play_game()
