### Source 
#The fighting game in the first world was inspired by a github repository (source: https://github.com/orkslayergamedev/python-classes-text-battle/tree/master and https://www.youtube.com/watch?v=cM_ocyOrs_k). This code was implemented and edited to fit into the fighting scene.

# ------------ Imports ------------

from weapon import fists
from health_bar import HealthBar


# ------------ Character class setup ------------

class Character:
    # Initializing method: attributes of the objects
    def __init__(self,
                 name: str, # name should be string as data type
                 health: int, # health should be integer as data type
                 ) -> None:
        # Object-level variables
        self.name = name
        self.health = health
        self.health_max = health

        # Defines standard weapon
        self.weapon = fists

    # Function to attack 
    def attack(self, opponent) -> None:
        # Health reduces by the damage done by the weapon of the attacker
        opponent.health -= self.weapon.damage
        # Makes sure that health never goes below 0 (since 0 means you've lost)
        opponent.health = max(target.health, 0)
        # Updates the health of the opponent in the health bar
        opponent.health_bar.update()
        print(f"{self.name} dealt {self.weapon.damage} damage to "
              f"{opponent.name} with {self.weapon.name}")


# ------------ User as character setup ------------

class You(Character):
    # User has name and health defined beforehand as parameters (no weapon needs to be defined, so user can switch weapons)
    def __init__(self,
                 name: str, # name should be string as data type
                 health: int # health should be integer as data type
                 ) -> None:
        super().__init__(name=name, health=health)

        # Defines fists as default weapon
        self.default_weapon = self.weapon
        # Health bar of user is colored blue
        self.health_bar = HealthBar(self, color="blue")

    # Function to equip a weapon
    def equip(self, weapon) -> None:
        self.weapon = weapon
        print(f"{self.name} picked up the {self.weapon.name}!")


# ------------ Twin brother (from fighting scene in first world) as character setup ------------

class TwinBrother(Character):
    # Twin brother has name, health and weapon defined beforehand as attributes
    def __init__(self,
                 name: str, # name should be string as data type
                 health: int, # health should be integer as data type
                 weapon,
                 ) -> None:
        super().__init__(name=name, health=health)
        self.weapon = weapon

        # Health bar of twin brother is colored red
        self.health_bar = HealthBar(self, color="red")