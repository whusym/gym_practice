## Using Genetic Algorithm to play Bowling in Atari environment (OpenAI Gym)
## Codes partly benefited from https://gist.github.com/PuZZleDucK/4a6b877964a0e67648b88bee05eeebf2#file-atari-7-genetic-py


from __future__ import print_function
from __future__ import division
import random
import pickle
import gym

children_per_gen = 160  # how many mutations; two many won't help.
survivors_per_gen = 20  # maybe 16 is too low... But if we increase the survivors, suboptimal survirors will dominate the children generation.
generations = 1000
max_time = 3000
resume = False
render = False

def generate_genisis():
    # Generate an initial population
    #To finish the game with 10 hits. It's around 3000 max time. So each hit is around 300 (if the no one makes it at first time). So each action is around 150
    digits = 150
    genisis = ''.join(['%s' % random.choice(range(1, 6)) for n in range(digits)])
    return genisis

# def mutate_crossover(action_string_1, action_string_2):
#     '''
#     Crossover between a central point of the string sequence. (Single-point Crossover)
#     '''
#     shuffle_location_1 = random.choice(range(len(action_string_1)))
#     first_child = action_string_1[:shuffle_location] + action_string_2[shuffle_location:]
#     second_child = action_string_2[:shuffle_location] + action_string_1[shuffle_location:]
#     return first_child, second_child

def mutate_crossover(action_string_1, action_string_2):
    '''
    Crossover between two central points of the sequence (Two-point Crossover)
    '''
    shuffle_location_1 = random.choice(range(0, len(action_string_1) - 3))
    shuffle_location_2 = random.choice(range(shuffle_location_1 + 1, len(action_string_1) - 1))
    first_child = action_string_1[:shuffle_location_1] + action_string_2[shuffle_location_1: shuffle_location_2] + action_string_1[shuffle_location_2:]
    second_child = action_string_2[:shuffle_location_1] + action_string_1[shuffle_location_1: shuffle_location_2] + action_string_2[shuffle_location_2:]
    return first_child, second_child


def mutate_single(action_string):
    '''
    Mutation of a single string
    '''
    mutate_location = random.choice(range(len(action_string)))
    new_gene = random.choice(range(1, 6))   # So there is a chance it does not mutate at all.
    return action_string[:mutate_location] + str(new_gene) + action_string[mutate_location+1: ]

def get_survivors(gen):
    return gen[(0-survivors_per_gen):]

def sort_gen(gen):
    sorted_gen = sorted(gen, key=lambda tup: tup[0])
    return_gen = []
    for score, child in sorted_gen:
        return_gen.append(child)
    print ("  ::    top 5: {}".format(sorted_gen[-1]))
    for n in range(2, survivors_per_gen):
        print ("  ::         : {}".format(sorted_gen[0-n]))
    # print ("  ::         : {}".format(sorted_gen[-3]))
    # print ("  ::         : {}".format(sorted_gen[-4]))
    # print ("  ::         : {}".format(sorted_gen[-5]))
    return return_gen

def crossover_survivors(survivor_set):
    '''
    A better way would be to penalize the survivors with lower fitness (but still let them survive) and reward more to the survivors with higher fitness
    '''
    result_set = []
    if len(survivor_set) <= 1: # One single person cannot have child
        print ("Too few survivors!")
    elif len(survivor_set) % 2 != 0:   # The number of total parents has to be even
        survivor_set = survivor_set[:-1]
    for i in range(len(survivor_set[0::2])):  # crossover element of odd_index in the survivor set with the member after it
        result_set.extend(mutate_crossover(survivor_set[0::2][i], survivor_set[1::2][i])) # get two more elements in the set
    return result_set


if __name__ == '__main__':
    last_gen = [] # There is no parent in the beginning of the game. The next few lines of code are for checking the previously saved ones.
    if resume:
      last_gen = pickle.load(open('save.p', 'rb'))
    else:
        for child in range(children_per_gen):
            last_gen.append(generate_genisis())
    env = gym.make('Bowling-v0')
    env.reset()
    print ('Experiment with ' + str(children_per_gen) + ' children per gen and ' + str(survivors_per_gen) + ' survivors per gen.\n')
    for gen in range(generations):
        survivors = get_survivors(last_gen)
        # survivors_cross = crossover_survivors(survivors)
        this_gen = []
        for child in range(children_per_gen):
            # There may not be the same amount of children_per_gen and survivors, so we take the modulo. children_per_gen may be much
            # more than survivors. So this following statement makes sure of the variation among the survivors being mutated. Otherwise we can
            # randomly sample a survivor and mutate one of its genomes.
            survivors_cross = crossover_survivors(survivors)
            mutant = mutate_single (survivors_cross[child % len(survivors_cross)])
            annealing_time = 0
            while annealing_time <= ((generations - gen) // 8):
                #20 is arbitrarily selected here. Since in total there are 1000 generations. 20 means there are 49 single mutations in the beginning.
                #As time goes, the repetitions of single mutations become fewer.
                mutant = mutate_single (survivors_cross[child % len(survivors_cross)])
                annealing_time += 1
            obervation = env.reset()
            total_reward = 0
            number_of_actions = len(mutant)   # In this case, it's always the same -- 150.
            for time in range(max_time):
                if render: env.render()
                next_action = int(mutant[time % number_of_actions])
                # print next_action
                observation, reward, done, info = env.step(next_action)
                total_reward = total_reward + reward
                if done:   # Maybe this is not needed, because in the env of bowling, there is no Done state.
                    break
            print("  ::  mutant {}: {} -- {}.".format(str(child).zfill(3), mutant, total_reward))
            score_and_child = (total_reward, mutant)
            this_gen.append(score_and_child)
        print ("After " + str(gen) + " generations: \n")
        last_gen = sort_gen(this_gen)
        if generations % 100 == 0: pickle.dump(last_gen, open('save.p', 'wb'))
    env.monitor.close()
