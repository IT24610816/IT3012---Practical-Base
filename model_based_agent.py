class ModelBasedAgent:
    """
    Model-Based Agent:
    Uses memory to keep track of visited cells
    and previous actions.
    """

    def __init__(self):
        # Internal memory
        self.visited_cells = set()

        # Current estimated position
        self.position = [0, 0]

        # Last action performed
        self.last_action = None

        # Current direction
        self.direction = "Up"


    def update_state(self, percept):

        # Remember current location
        self.visited_cells.add(tuple(self.position))


    def move_tracker(self, action):

        # Update estimated position based on action

        if action == "Up":
            self.position[1] += 1

        elif action == "Down":
            self.position[1] -= 1

        elif action == "Left":
            self.position[0] -= 1

        elif action == "Right":
            self.position[0] += 1



    def sense_and_act(self, percept):

        # Update memory first
        self.update_state(percept)


        current = tuple(self.position)


        # Rule 1:
        # If food exists, collect it
        if percept["food_here"]:
            action = "Suck"


        # Rule 2:
        # If wall ahead, avoid repeating previous path
        elif percept["wall_ahead"]:

            # Try turning right if stuck
            action = "Right"


        # Rule 3:
        # If we have already visited this area,
        # choose a different direction
        elif current in self.visited_cells:

            action = "Right"


        # Default: continue forward
        else:
            action = "Up"


        # Store last action in memory
        self.last_action = action

        # Update internal movement model
        self.move_tracker(action)

        return action