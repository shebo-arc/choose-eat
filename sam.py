def select(self, node):
    # Select a child node based on the UCB formula until a node that is not fully expanded is found
    while node.is_fully_expanded(self.available_food_items):
        node = node.best_child()
    return node