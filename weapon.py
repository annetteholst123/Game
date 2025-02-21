# ------------ class setup ------------
class Weapon:
    def __init__(self,
                 name: str,
                 damage: int
                 ) -> None:
        self.name = name
        self.damage = damage


# ------------ object creation ------------
sword = Weapon(name="Sword",
                    damage=5)

pan = Weapon(name="Pan",
                   damage=7)

fists = Weapon(name="Fists",
               damage=3)