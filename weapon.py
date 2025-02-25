### Source 
#The fighting game in the first world was inspired by a github repository (source: https://github.com/orkslayergamedev/python-classes-text-battle/tree/master and https://www.youtube.com/watch?v=cM_ocyOrs_k). This code was implemented and edited to fit into the fighting scene.

# ------------ Weapon class setup ------------

class Weapon:
    # Attributes of weapon are name and damage
    def __init__(self,
                 name: str, # name should be string as data type
                 damage: int # damage done by attack should be integer as data type
                 ) -> None:
        # Defining the attributes
        self.name = name
        self.damage = damage


# ------------ Creating objects ------------

# Object sword has damage 5
sword = Weapon(name="Sword",
                    damage=5)

# Object pan has damage 7
pan = Weapon(name="Pan",
                   damage=7)

# Default weapon (fists) has damage 3
fists = Weapon(name="Fists",
               damage=3)