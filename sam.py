import csv
import math
import random


class Destination:
    def __init__(self, name, cost, rating, rating_weight, cost_weight, parent=None):
        self.name = name
        self.cost = cost
        self.rating = rating
        self.rating_weight = rating_weight
        self.cost_weight = cost_weight
        self.visits = 0  # Initialize visit count (how many times this destination has been visited)
        self.wins = 0  # Initialize win count (sum of ratings from simulations)
        self.children = []  # List to store child nodes (destinations that can be explored)
        self.parent = parent  # Keep track of the parent node for backpropagation


def ucb_score(total_visits, node_wins, parent_visits, exploration_param):
    if total_visits == 0:
        return float('inf')  # If a node has never been visited, it should be explored
    return (node_wins / total_visits) + exploration_param * math.sqrt(math.log(parent_visits) / total_visits)


def select_best_child(node, exploration_param):
    best_score = -float('inf')
    best_child = None
    for child in node.children:
        score = ucb_score(child.visits, child.wins, node.visits, exploration_param)
        if score > best_score:
            best_score = score
            best_child = child
    return best_child


def simulate(destination):
    # Simulate a weighted outcome based on the destination's rating and cost
    rating_score = destination.rating * destination.rating_weight
    cost_score = (1 / destination.cost) * destination.cost_weight  # Inversely proportional to cost
    return random.uniform(0, rating_score + cost_score)


def expand_node(node, destinations):
    # Expand the node by creating children that haven't been explored yet
    for dest in destinations:
        if not any(child.name == dest.name for child in node.children):
            node.children.append(
                Destination(dest.name, dest.cost, dest.rating, dest.rating_weight, dest.cost_weight, parent=node))


def mcts_choose_destination(destinations, iterations):
    root = Destination('Root', 0, 0, 0, 0)
    expand_node(root, destinations)  # Initialize root with possible destinations

    for _ in range(iterations):
        node = root
        # Selection and Expansion
        while node.children:
            if all(child.visits > 0 for child in node.children):
                node = select_best_child(node, math.sqrt(2))  # Exploration parameter (adjustable)
            else:
                expand_node(node, destinations)
                node = random.choice([child for child in node.children if child.visits == 0])
                break

        # Simulation: simulate the outcome of choosing this destination
        simulation_result = simulate(node)

        # Backpropagation
        while node:
            node.visits += 1
            node.wins += simulation_result
            node = node.parent

    # Choose the destination with the highest average result
    best_destination = max(root.children, key=lambda x: x.wins / x.visits)

    return best_destination.name


def load_destinations_from_csv(csv_filename):
    destinations = []
    with open(csv_filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row['name']
            cost = float(row['cost'])
            rating = float(row['rating'])
            rating_weight = float(row['rating_weight'])
            cost_weight = float(row['cost_weight'])
            destinations.append(Destination(name, cost, rating, rating_weight, cost_weight))
    return destinations


# Example usage
if __name__ == "__main__":
    # Load destinations from CSV file
    csv_filename = 'destinations.csv'
    destinations = load_destinations_from_csv(csv_filename)

    # Run MCTS with 1000 iterations using the data from the CSV
    chosen_destination = mcts_choose_destination(destinations, 1000)
    print(f"The recommended destination is: {chosen_destination}")
