### Source 
#The fighting game in the first world was inspired by a github repository (source: https://github.com/orkslayergamedev/python-classes-text-battle/tree/master and https://www.youtube.com/watch?v=cM_ocyOrs_k). This code was implemented and edited to fit into the fighting scene.

# ------------ Import ------------
import os

# ------------ Set up ------------

# Call os' system method with an empty command (in case console doesn't print colors properly)
os.system("")


# ------------ Class health bar setup ------------

class HealthBar:
    # Symbols and decorating barriers (defined on class level)
    symbol_remaining: str = "█"
    symbol_lost: str = "_"
    barrier: str = "|"
    # Color values that are stored into a dictionary
    colors: dict = {"red": "\033[91m",
                    "blue": "\33[34m",
                    "default": "\033[0m"
                    }

    def __init__(self,
                 entity,
                 length: int = 20, # Default length is 20
                 is_colored: bool = True,
                 color: str = "") -> None:
        # Attributes of health bar
        self.entity = entity
        self.length = length
        # Defining max value of health bar while referring to entity 
        self.max_value = entity.health_max
        # Defining current value of health bar while referring to entity
        self.current_value = entity.health
        self.is_colored = is_colored
        # Find colour key in dictionary and its corresponding value; 
        #if the color is not in the colour key, 
        #then the default colour is used for the health bar
        self.color = self.colors.get(color) or self.colors["default"]

    # Update method to update the current value of the health bar
    def update(self) -> None:
        # Set current value of health bar to health of its entity
        self.current_value = self.entity.health

    # Drawing method to print the health bar to the screen
    def draw(self) -> None:
        # Remaining bar amount of health bar is 
        # length multiplied by ratio of current and max values
        remaining_bars = round(self.current_value / self.max_value * self.length)
        # Lost bars = length of health bar - remaining bars
        lost_bars = self.length - remaining_bars
        # Print health with numbers
        print(f"{self.entity.name}'s HEALTH: {self.entity.health}/{self.entity.health_max}")
        # Print the health bar with colours 
        print(f"{self.barrier}"
              f"{self.color if self.is_colored else ''}"
              f"{remaining_bars * self.symbol_remaining}"
              f"{lost_bars * self.symbol_lost}"
              f"{self.colors['default'] if self.is_colored else ''}"
              f"{self.barrier}")