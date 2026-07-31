class SimpleReflexAgent:
    
    #A simple reflex agent that makes decisions using only the current percept.
    

    def sense_and_act(self, percept):

        # Rule 1: If food is here, collect it
        if percept["food_here"]:
            return "Suck"

        # Rule 2: If there is a wall ahead, turn left
        if percept["wall_ahead"]:
            return "Left"

        # Rule 3: Otherwise, keep moving forward
        return "Up"