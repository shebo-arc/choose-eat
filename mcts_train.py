import csv
import math
import random
import pandas as pd


# Function to read food data from CSV
def read_food_data_from_csv(file_path):
    food_items = []
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            food_name = row['food_name']
            calories = float(row['cal_per_serving'])
            energy = float(row['kj_per_serving'])  # Energy in kilojoules
            food_items.append(FoodItem(food_name, calories, energy))
    return food_items


def data_prune(file_path, foods):
    df = pd.read_csv(file_path)
    food_list = [
        "Fruit Juices", "Alcoholic Drinks & Beverages", "Beef & Veal",
        "Beer", "Cakes & Pies", "Cereal Products", "Cold Cuts & Lunch Meat",
        "Dishes & Meals", "Fast Food", "Fish & Seafood", "Fruits",
        "Ice Cream", "Legumes", "Meat", "Milk & Dairy Products",
        "Non-Alcoholic Drinks & Beverages", "Pasta & Noodles",
        "Pastries, Breads & Rolls", "Pizza", "Pork",
        "Potato Products", "Poultry & Fowl", "Soups",
        "Tropical & Exotic Fruits", "Venison & Game", "Wine"
    ]

    for food in foods:
        food_list.remove(food)

    for name in food_list:
        df = df[df['food_category'] != name]

    df.to_csv('pruned.csv')


# Function to get weights for calories and energy from the user, and normalize them
def get_user_weights():
    calorie_weight = float(input("Enter weight for calories (higher means minimizing calories is more important): "))
    energy_weight = float(input("Enter weight for energy (higher means maximizing energy is more important): "))

    # Normalize the weights so that their sum equals 1
    total_weight = calorie_weight + energy_weight
    normalized_calorie_weight = calorie_weight / total_weight
    normalized_energy_weight = energy_weight / total_weight

    return normalized_calorie_weight, normalized_energy_weight


# Class for food items
class FoodItem:
    def __init__(self, name, calories, energy):
        self.name = name
        self.calories = calories
        self.energy = energy


# Class representing each node in the MCTS
class Node:
    def __init__(self, state, parent=None, food_item=None):
        self.state = state  # (calories, energy, food_list)
        self.parent = parent
        self.food_item = food_item
        self.children = []
        self.visits = 0
        self.total_reward = 0

    def is_fully_expanded(self, available_food_items):
        # Node is fully expanded when all food items have been tried
        return len(self.children) == len(available_food_items)

    def best_child(self, exploration_param=1.41):
        # Select the child node with the highest UCB value
        best_value = float('-inf')
        best_node = None

        for child in self.children:
            ucb_value = (child.total_reward / child.visits) + exploration_param * math.sqrt(
                math.log(self.visits) / child.visits)
            if ucb_value > best_value:
                best_value = ucb_value
                best_node = child

        return best_node


# Class implementing Monte Carlo Tree Search (MCTS)
class MCTS:
    def __init__(self, available_food_items, calorie_limit, simulations):
        self.available_food_items = available_food_items
        self.calorie_limit = calorie_limit
        self.simulations = simulations

    def expand(self, node):
        # Expand the current node by adding a child node for each food item not yet tried
        for food_item in self.available_food_items:
            if all(c.food_item != food_item for c in node.children):
                new_calories = node.state[0] + food_item.calories
                new_energy = node.state[1] + food_item.energy

                if new_calories <= self.calorie_limit:
                    new_state = (new_calories, new_energy, node.state[2] + [food_item])
                    child_node = Node(state=new_state, parent=node, food_item=food_item)
                    node.children.append(child_node)

    def simulate(self, node, calorie_weight, energy_weight):
        calories, energy, food_list = node.state
        remaining_food = [f for f in self.available_food_items if f not in food_list]

        total_calories = calories
        total_energy = energy

        # Randomly pick food until we exceed the calorie limit or run out of valid options
        while remaining_food and total_calories <= self.calorie_limit:
            food = random.choice(remaining_food)
            remaining_food.remove(food)

            if total_calories + food.calories <= self.calorie_limit:
                total_calories += food.calories
                total_energy += food.energy

        # Direct scoring - minimize calories and maximize energy based on weights
        weighted_score = (calorie_weight * (-total_calories)) + (energy_weight * total_energy)

        return weighted_score

    def select(self, node):
        # Randomly choose to explore more if random.random() < 0.1: # 10% chance to select a random child
        if random.random() < 0.1:
            return random.choice(node.children) if node.children else node

        while node.is_fully_expanded(self.available_food_items):
            node = node.best_child()

        return node

    def backpropagate(self, node, reward):
        # Back propagate the reward up the tree
        while node:
            node.visits += 1
            node.total_reward += reward
            node = node.parent

    def run(self, calorie_weight, energy_weight):
        root = Node(state=(0, 0, []))  # (calories, energy, food_list)

        # Ensure the root is expanded before starting simulations
        if not root.children:
            self.expand(root)

        for _ in range(self.simulations):
            node = self.select(root)
            if not node.is_fully_expanded(self.available_food_items):
                self.expand(node)
            reward = self.simulate(node, calorie_weight, energy_weight)  # Pass weights to simulate
            self.backpropagate(node, reward)

        # Record all explored nodes into data.csv
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Calories', 'Energy', 'Food List', 'Visits', 'Total Reward'])  # Header

            # Write all nodes including root and children
            nodes_to_write = [root] + root.children
            for node in nodes_to_write:
                writer.writerow([node.state[0], node.state[1], [food.name for food in node.state[2]], node.visits,
                                 node.total_reward])

        # Best action from the root node; ensure there are children before proceeding.
        if not root.children:
            raise ValueError("No valid food choices were generated.")

        best_child = max(root.children, key=lambda c: c.visits)
        print(best_child)

        # Return the best sequence of food items.
        return best_child.state[2]

'''
# Main program to test the MCTS implementation.
if __name__ == "__main__":
    # Clearing the data file each time.
    with open('data.csv', 'w') as file:
        pass

    print("cleared the file")

    # Read food data from CSV file.
    csv_file_path = 'filtered_food_data.csv'  # Path to your CSV file.

    foods_to_prune = ["Wine"]

    data_prune(csv_file_path, foods_to_prune)  # Prune unwanted foods.

    available_food_items = read_food_data_from_csv('pruned.csv')  # Read pruned data.

    # Get user-defined weights for calories and energy (normalized to sum to 1).
    calorie_weight, energy_weight = get_user_weights()

    # Set the calorie limit.
    calorie_limit = 100

    # Create MCTS instance.
    mcts_instance = MCTS(available_food_items, calorie_limit, simulations=1000)

    # Run MCTS to find the best food plan.
    best_food_plan = mcts_instance.run(calorie_weight, energy_weight)

    # Print the best food plan.
    print("Best food plan to maximize the score under calorie limit:")

    for food in best_food_plan:
        print(f"{food.name} - Calories: {food.calories}, Energy: {food.energy}")
'''
