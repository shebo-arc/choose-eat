import csv
import math
import random

# Function to read food data from CSV
# Reads the file and creates a list of FoodItem objects.
def read_food_data_from_csv(file_path):
    food_items = []
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            food_name = row['food_name']
            calories = float(row['cal_per_serving'])
            energy = float(row['kj_per_serving'])  # Energy in kilojoules
            # Create FoodItem instances and add them to the list
            food_items.append(FoodItem(food_name, calories, energy))
    return food_items


# Function to get weights for calories and energy from the user, and normalize them
# Allows the user to specify importance for calories and energy, then normalizes the weights.
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
        self.state = state  # (calories, energy, food_list) representing the current state
        self.parent = parent  # The parent node
        self.food_item = food_item  # The food item represented by this node
        self.children = []  # List of child nodes
        self.visits = 0  # Number of times the node has been visited
        self.total_reward = 0  # Total accumulated reward for this node

    # Check if all available food items have been tried (node is fully expanded)
    def is_fully_expanded(self, available_food_items):
        return len(self.children) == len(available_food_items)

    # Select the best child node using the UCB formula
    def best_child(self, exploration_param=1.41):
        best_value = float('-inf')  # Set to a very small number initially
        best_node = None

        # Iterate over all child nodes to find the one with the highest UCB value
        for child in self.children:
            ucb_value = (child.total_reward / (child.visits + 1e-5)) + exploration_param * math.sqrt(
                math.log(self.visits + 1) / (child.visits + 1e-5))
            if ucb_value > best_value:
                best_value = ucb_value
                best_node = child

        return best_node  # Return the child node with the best UCB value


# Class implementing Monte Carlo Tree Search (MCTS)
class MCTS:
    def __init__(self, available_food_items, calorie_limit, simulations):
        self.available_food_items = available_food_items  # List of all available food items
        self.calorie_limit = calorie_limit  # Maximum calorie intake allowed
        self.simulations = simulations  # Number of simulations to run

    # Expands the current node by adding a child node for each food item that hasn't been tried yet
    def expand(self, node):
        # Iterate over available food items
        for food_item in self.available_food_items:
            #print(food_item.calories)  # Debugging: Print calorie value of the current food item

            # Ensure that the food item hasn't already been added as a child
            if all(c.food_item != food_item for c in node.children):
                new_calories = node.state[0] + food_item.calories  # Update total calories
                new_energy = node.state[1] + food_item.energy  # Update total energy

                # Only expand if the new total calories don't exceed the limit
                if new_calories <= self.calorie_limit:
                    # Create a new state (calories, energy, food_list)
                    new_state = (new_calories, new_energy, node.state[2] + [food_item])
                    # Create the new child node with the updated state
                    child_node = Node(state=new_state, parent=node, food_item=food_item)
                    node.children.append(child_node)  # Append the new child to the parent's children list
                    return child_node  # Return the newly created child node

    # Select a node based on the UCB formula until a non-fully expanded node is found
    def select(self, node):
        #print(len(node.children))
        while node.is_fully_expanded(self.available_food_items) and node.children:
            node = node.best_child()  # Select the best child node using UCB formula
        return node

    # Simulate a possible outcome by randomly picking food items until the calorie limit is reached
    def simulate(self, node, calorie_weight, energy_weight):
        # Start with the current state of the node
        calories, energy, food_list = node.state
        remaining_food = [f for f in self.available_food_items if f not in food_list]

        total_calories = calories
        total_energy = energy

        # Randomly pick food until we exceed the calorie limit or run out of valid options
        while remaining_food and total_calories <= self.calorie_limit:
            food = random.choice(remaining_food)  # Randomly select a food item
            remaining_food.remove(food)  # Remove the chosen food from the remaining list

            # Only add the food if it doesn't exceed the calorie limit
            if total_calories + food.calories <= self.calorie_limit:
                total_calories += food.calories
                total_energy += food.energy

        # Normalize the calories and energy
        max_energy = max(f.energy for f in self.available_food_items)  # Find the maximum possible energy
        normalized_calories = total_calories / self.calorie_limit  # Scale calories between 0 and 1
        normalized_energy = total_energy / max_energy  # Scale energy between 0 and 1

        # Calculate the weighted score (higher energy is better, fewer calories is better)
        weighted_score = (energy_weight * normalized_energy) - (calorie_weight * normalized_calories ** 2)

        return weighted_score

    # Backpropagate the reward through the tree (updating the visit count and reward)
    def backpropagate(self, node, reward):
        while node:
            node.visits += 1  # Increment the visit count
            node.total_reward += reward  # Add the reward to the node's total reward
            node = node.parent  # Move up to the parent node

    # Run the MCTS algorithm
    def run(self, calorie_weight, energy_weight):
        root = Node(state=(0, 0, []))  # Root node with zero calories and energy

        # Expand the root node before starting simulations
        self.expand(root)
        print("expanded")  # Debugging: Confirm that the root node has been expanded

        # Run multiple simulations
        for _ in range(self.simulations):
            node = self.select(root)  # Select a node for simulation
            if not node.is_fully_expanded(self.available_food_items):
                node = self.expand(node)  # Expand the selected node if it's not fully expanded
            reward = self.simulate(node, calorie_weight, energy_weight)  # Simulate to get a reward
            self.backpropagate(node, reward)  # Backpropagate the reward up the tree

        # Ensure that the root has children, and pick the best one based on visit count
        if not root.children:
            raise ValueError("No valid food choices were generated.")  # Handle the error if no children exist

        best_child = max(root.children, key=lambda c: c.visits)  # Select the child with the most visits
        print(best_child)  # Debugging: Print the best child node
        print(best_child.state)  # Debugging: Print the best food list
        return best_child.state[2]  # Return the best sequence of food items


# Main program to test the MCTS implementation
if __name__ == "__main__":

    csv_file_path = 'filtered_food_data.csv'
    available_food_items = read_food_data_from_csv(csv_file_path)
    calorie_weight, energy_weight = get_user_weights()
    calorie_limit = 3000


    mcts = MCTS(available_food_items, calorie_limit, simulations=500)
    print("checkpoint 1")

    # Run MCTS to find the best food plan
    best_food_plan = mcts.run(calorie_weight, energy_weight)
    print("checkpoint 2")

    print("Best food plan to maximize the score under calorie limit:")
    for food in best_food_plan:
        print(f"{food.name} - Calories: {food.calories}, Energy: {food.energy}")

