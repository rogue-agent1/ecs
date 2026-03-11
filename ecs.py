#!/usr/bin/env python3
"""ecs — Entity Component System game architecture. Zero deps."""

class World:
    def __init__(self):
        self._next_id = 0
        self._components = {}  # comp_type -> {entity_id: component}
        self._systems = []

    def create_entity(self):
        eid = self._next_id; self._next_id += 1; return eid

    def add_component(self, entity, component):
        ctype = type(component)
        self._components.setdefault(ctype, {})[entity] = component

    def get_component(self, entity, ctype):
        return self._components.get(ctype, {}).get(entity)

    def query(self, *ctypes):
        if not ctypes: return
        first = self._components.get(ctypes[0], {})
        for eid in first:
            comps = [first[eid]]
            for ct in ctypes[1:]:
                c = self._components.get(ct, {}).get(eid)
                if c is None: break
                comps.append(c)
            else:
                yield eid, tuple(comps)

    def add_system(self, system):
        self._systems.append(system)

    def update(self, dt):
        for system in self._systems:
            system(self, dt)

class Position:
    def __init__(self, x=0, y=0): self.x, self.y = x, y
    def __repr__(self): return f"Pos({self.x:.1f},{self.y:.1f})"

class Velocity:
    def __init__(self, vx=0, vy=0): self.vx, self.vy = vx, vy

class Health:
    def __init__(self, hp=100): self.hp = self.max_hp = hp

class Name:
    def __init__(self, name): self.name = name

def movement_system(world, dt):
    for eid, (pos, vel) in world.query(Position, Velocity):
        pos.x += vel.vx * dt
        pos.y += vel.vy * dt

def damage_system(world, dt):
    for eid, (health,) in world.query(Health):
        if health.hp <= 0:
            name = world.get_component(eid, Name)
            n = name.name if name else f"Entity {eid}"
            print(f"  💀 {n} has died!")

def main():
    world = World()
    world.add_system(movement_system)
    p1 = world.create_entity()
    world.add_component(p1, Name("Hero"))
    world.add_component(p1, Position(0, 0))
    world.add_component(p1, Velocity(1, 0.5))
    world.add_component(p1, Health(100))
    p2 = world.create_entity()
    world.add_component(p2, Name("Enemy"))
    world.add_component(p2, Position(10, 10))
    world.add_component(p2, Velocity(-1, -1))
    world.add_component(p2, Health(50))
    print("ECS Simulation:")
    for tick in range(5):
        world.update(1.0)
        print(f"  Tick {tick+1}:")
        for eid, (name, pos) in world.query(Name, Position):
            hp = world.get_component(eid, Health)
            print(f"    {name.name}: {pos} HP={hp.hp if hp else '?'}")

if __name__ == "__main__":
    main()
