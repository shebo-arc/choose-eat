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

def data_prune(file_path):
    df = pd.read_csv(file_path)
    list = ["Fruit Juices", "Alcoholic Drinks & Beverages", "Beef & Veal", "Beer", "Cakes & Pies", "Cereal Products",
    "Cold Cuts & Lunch Meat",
    "Dishes & Meals",
    "Fast Food",
    "Fish & Seafood",
    "Fruits",
    "Ice Cream",
    "Legumes",
    "Meat",
    "Milk & Dairy Products",
    "Non-Alcoholic Drinks & Beverages",
    "Pasta & Noodles",
    "Pastries, Breads & Rolls",
    "Pizza",
    "Pork",
    "Potato Products",
    "Poultry & Fowl",
    "Soups",
    "Tropical & Exotic Fruits",
    "Venison & Game",]
    for name in list:
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
            ucb_value = (child.total_reward / (child.visits + 1e-5)) + exploration_param * math.sqrt(
                math.log(self.visits + 1) / (child.visits + 1e-5))
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

    def select(self, node):
        # Select a child node based on the UCB formula until a node that is not fully expanded is found
        while node.is_fully_expanded(self.available_food_items):
            node = node.best_child()
        return node

    def simulate(self, node, calorie_weight, energy_weight):
        # Start with the current state of the node (calories, energy, food_list)
        calories, energy, food_list = node.state
        remaining_food = [f for f in self.available_food_items if f not in food_list]

        total_calories = calories
        total_energy = energy

        # Randomly pick food until we exceed the calorie limit or run out of valid options
        while remaining_food and total_calories <= self.calorie_limit:
            # Introducing randomness in food selection
            if random.random() < 0.5:  # 50% chance to pick a random food
                food = random.choice(remaining_food)
            else:  # 50% chance to pick the food with the highest energy
                food = max(remaining_food, key=lambda f: f.energy)

            remaining_food.remove(food)  # Remove the chosen food from the remaining food list

            if total_calories + food.calories <= self.calorie_limit:
                total_calories += food.calories
                total_energy += food.energy

        # Normalize calories and energy
        max_energy = max(f.energy for f in self.available_food_items)  # Maximum possible energy
        normalized_calories = total_calories / self.calorie_limit  # Value between 0 and 1
        normalized_energy = total_energy / max_energy  # Value between 0 and 1

        # Revised scoring logic
        weighted_score = (energy_weight * normalized_energy) - (calorie_weight * normalized_calories ** 2)

        return weighted_score

    def select(self, node):
        # Randomly choose to explore more
        if random.random() < 0.1:  # 10% chance to select a random child
            return random.choice(node.children) if node.children else node
        while node.is_fully_expanded(self.available_food_items):
            node = node.best_child()
        return node

    def backpropagate(self, node, reward):
        # Backpropagate the reward up the tree
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
            if node.is_fully_expanded(self.available_food_items):
                node = self.expand(node)
            reward = self.simulate(node, calorie_weight, energy_weight)  # Pass weights to simulate
            self.backpropagate(node, reward)

        # Best action from the root node, ensure there are children
        if not root.children:
            raise ValueError("No valid food choices were generated.")
        else:
            for child in root.children:
                data = [child.state,child.visits,child.total_reward]
                with open('data.csv', 'a') as file:
                    writer = csv.writer(file)
                    writer.writerow(data)

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.state[2]  # Return the best sequence of food items


# Main program to test the MCTS implementation
if __name__ == "__main__":
    # clearing the data file each time
    with open('data.csv', 'w') as file:
        pass
    print("cleared the file")

    # Read food data from CSV file
    csv_file_path = 'filtered_food_data.csv'  # Path to your CSV file
    data_prune(csv_file_path)
    available_food_items = read_food_data_from_csv('pruned.csv')

    # Get user-defined weights for calories and energy (normalized to sum to 1)
    calorie_weight, energy_weight = get_user_weights()

    # Set the calorie limit
    calorie_limit = 100

    # Create MCTS instance
    mcts = MCTS(available_food_items, calorie_limit, simulations=1000)

    # Run MCTS to find the best food plan
    best_food_plan = mcts.run(calorie_weight, energy_weight)

    # Print the best food plan
    print("Best food plan to maximize the score under calorie limit:")
    for food in best_food_plan:
        print(f"{food.name} - Calories: {food.calories}, Energy: {food.energy}")