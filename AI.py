import matplotlib.pyplot as plt
import torch
from NeuralNet import *
import numpy as np
from copy import deepcopy
from tqdm import tqdm
from game import *

if __name__ == "__main__":

    # for reproducibility
    my_seed = 2786
    np.random.seed(my_seed)
    torch.manual_seed(my_seed)

    # View good score games while training ?
    view_games = True

    # Stats for plotting
    loss_means = []
    highest_scores = []
    best_play_models = []

    # Initial run 1
    nr_agents = 100000
    agents = []
    losses = []
    scores = []
    for agent in tqdm(range(nr_agents)):
        net = NeuralNetwork(seed=my_seed+agent)
        theApp = SimpleSnakeApp(seed=my_seed+agent,
                                neural_net=net,
                                display_gameplay=False)
        theApp.on_execute()
        scores.append(theApp.current_score)
        losses.append(theApp.loss)
        agents.append(net)

    fig, ax = plt.subplots(1, 1, figsize=(10,5))
    iterations = [i + 1 for i in range(len(agents))]
    ax.plot(iterations, losses)
    ax.plot(iterations, losses, 'o', ms=1)
    ax.set_xlabel("Agent nr.")
    ax.set_ylabel("Loss")
    plt.savefig("generation_losses/" + str(0) + "_generation.pdf")
    plt.cla()
    plt.clf()
    plt.close()

    print("highest score: ", np.max(scores))
    highest_scores.append(np.max(scores))
    loss_means.append(np.mean(losses))

    # Generation training
    nr_generations = 30
    nr_best = 1  # int(len(agents)/100)  # try with 1
    lr = 0.0001
    for generation in range(nr_generations):

        # Picking out 'nr_best' agents and adding some mutation
        best_agents = np.array(agents)[np.argsort(np.array(losses))][:nr_best]
        agents = [a for a in best_agents]
        nr_mutations = int((nr_agents/1000 - nr_best) / len(best_agents))
        for best_agent in best_agents:
            for mutation in range(nr_mutations):
                mutated_agent = deepcopy(best_agent)
                for layer_name in mutated_agent.state_dict():
                    if "weight" not in layer_name and 'bias' not in layer_name:
                        continue
                    mutated_agent.state_dict()[layer_name] += lr * torch.normal(mean=0, std=torch.ones(size=mutated_agent.state_dict()[layer_name].shape))
                    # mutated_agent.state_dict()[layer_name] += lr*torch.rand(size=mutated_agent.state_dict()[layer_name].shape)
                    # mutated_agent.state_dict()[layer_name] += lr * torch.bernoulli(torch.abs(mutated_agent.state_dict()[layer_name]))
                agents.append(mutated_agent)

        losses = []
        scores = []
        for agent in tqdm(range(len(agents))):
            theApp = SimpleSnakeApp(seed=my_seed+len(agents)*generation+agent,
                                    neural_net=agents[agent],
                                    display_gameplay=False)
            theApp.on_execute()
            losses.append(theApp.loss)
            scores.append(theApp.current_score)
            if theApp.current_score >= 55:
                print("current score: ", theApp.current_score)
                agents[agent].save_model(score=theApp.current_score)
            if theApp.current_score >= 65:
                print("Playing game w. score: ", theApp.current_score)
                if view_games:
                    theApp = SimpleSnakeApp(seed=my_seed+len(agents)*generation+agent,
                                            neural_net=agents[agent],
                                            display_gameplay=True)
                    theApp.on_execute()

        loss_means.append(np.mean(losses))
        best_play_models.append(np.array(losses)[np.argmin(losses)])
        highest_scores.append(np.max(scores))

        print("generation: ", generation + 1)
        print("highest score: ", np.max(scores))

        fig, ax = plt.subplots(1,1,figsize=(10,5))
        iterations = [i + 1 for i in range(len(losses))]
        ax.plot(iterations, losses)
        ax.plot(iterations, losses, 'o', ms=1)
        ax.set_xlabel("Agent nr.")
        ax.set_ylabel("Loss")
        plt.savefig("generation_losses/" + str(generation + 1) + "_generation.pdf")
        plt.cla()
        plt.clf()
        plt.close()

    generations = [i + 1 for i in range(len(loss_means))]
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(generations, loss_means)
    ax.plot(generations, loss_means, 'o', ms=1)
    ax.set_xlabel("Generation nr.")
    ax.set_ylabel("Avg. loss")
    plt.savefig("generation_losses/" + "loss_means.pdf")
    plt.cla()
    plt.clf()
    plt.close()

    generations = [i + 1 for i in range(len(highest_scores))]
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.plot(generations, highest_scores)
    ax.plot(generations, highest_scores, 'o', ms=1)
    ax.set_xlabel("Generation nr.")
    ax.set_ylabel("Highest score")
    plt.savefig("generation_losses/" + "highest_scores.pdf")

