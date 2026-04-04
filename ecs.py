#!/usr/bin/env python3
"""ecs - Entity Component System game engine pattern (entities, components, systems, queries)."""

import sys, json, time
from collections import defaultdict

class World:
    def __init__(self):
        self.next_id = 0
        self.entities = {}  # id -> set of component types
        self.components = defaultdict(dict)  # type -> {entity_id: data}
        self.systems = []

    def spawn(self, **components):
        eid = self.next_id; self.next_id += 1
        self.entities[eid] = set()
        for ctype, data in components.items():
            self.entities[eid].add(ctype)
            self.components[ctype][eid] = data
        return eid

    def despawn(self, eid):
        for ctype in self.entities.get(eid, set()):
            self.components[ctype].pop(eid, None)
        self.entities.pop(eid, None)

    def add_component(self, eid, ctype, data):
        self.entities[eid].add(ctype)
        self.components[ctype][eid] = data

    def remove_component(self, eid, ctype):
        self.entities[eid].discard(ctype)
        self.components[ctype].pop(eid, None)

    def get(self, eid, ctype):
        return self.components[ctype].get(eid)

    def set(self, eid, ctype, data):
        self.components[ctype][eid] = data

    def query(self, *ctypes):
        """Find all entities with ALL specified components."""
        if not ctypes: return []
        result = []
        candidates = set(self.components[ctypes[0]].keys())
        for ct in ctypes[1:]:
            candidates &= set(self.components[ct].keys())
        for eid in candidates:
            comps = {ct: self.components[ct][eid] for ct in ctypes}
            result.append((eid, comps))
        return result

    def add_system(self, fn, priority=0):
        self.systems.append((priority, fn))
        self.systems.sort(key=lambda x: x[0])

    def tick(self, dt=1.0):
        for _, system_fn in self.systems:
            system_fn(self, dt)

    def stats(self):
        ctypes = set()
        for eid, types in self.entities.items():
            ctypes.update(types)
        return {
            'entities': len(self.entities),
            'component_types': len(ctypes),
            'components': sum(len(v) for v in self.components.values()),
            'systems': len(self.systems),
        }

def cmd_demo(args):
    world = World()

    # spawn entities
    player = world.spawn(
        position={'x': 0, 'y': 0},
        velocity={'x': 1, 'y': 0.5},
        health={'hp': 100, 'max_hp': 100},
        name={'value': 'Hero'}
    )
    enemy1 = world.spawn(
        position={'x': 10, 'y': 5},
        velocity={'x': -0.5, 'y': 0},
        health={'hp': 50, 'max_hp': 50},
        name={'value': 'Goblin'}
    )
    enemy2 = world.spawn(
        position={'x': -5, 'y': 8},
        health={'hp': 30, 'max_hp': 30},
        name={'value': 'Slime'}
    )
    tree = world.spawn(
        position={'x': 3, 'y': 3},
        name={'value': 'Tree'}
    )

    # systems
    def movement_system(w, dt):
        for eid, comps in w.query('position', 'velocity'):
            pos = comps['position']
            vel = comps['velocity']
            pos['x'] += vel['x'] * dt
            pos['y'] += vel['y'] * dt
            w.set(eid, 'position', pos)

    def combat_system(w, dt):
        entities = w.query('position', 'health')
        for i, (eid1, c1) in enumerate(entities):
            for eid2, c2 in entities[i+1:]:
                dx = c1['position']['x'] - c2['position']['x']
                dy = c1['position']['y'] - c2['position']['y']
                dist = (dx**2 + dy**2)**0.5
                if dist < 2:
                    c2['health']['hp'] -= 5
                    w.set(eid2, 'health', c2['health'])

    world.add_system(movement_system, priority=1)
    world.add_system(combat_system, priority=2)

    print("=== ECS Demo ===\n")
    print(f"Stats: {world.stats()}\n")

    # print initial state
    print("Initial state:")
    for eid, comps in world.query('name', 'position'):
        name = comps['name']['value']
        pos = comps['position']
        health = world.get(eid, 'health')
        hp_str = f" HP:{health['hp']}/{health['max_hp']}" if health else ""
        print(f"  [{eid}] {name} at ({pos['x']:.1f}, {pos['y']:.1f}){hp_str}")

    # simulate 5 ticks
    for tick in range(5):
        world.tick(dt=1.0)

    print(f"\nAfter 5 ticks:")
    for eid, comps in world.query('name', 'position'):
        name = comps['name']['value']
        pos = comps['position']
        health = world.get(eid, 'health')
        hp_str = f" HP:{health['hp']}/{health['max_hp']}" if health else ""
        print(f"  [{eid}] {name} at ({pos['x']:.1f}, {pos['y']:.1f}){hp_str}")

    # query examples
    print(f"\nEntities with health: {len(world.query('health'))}")
    print(f"Moving entities: {len(world.query('position', 'velocity'))}")
    print(f"Static entities: {len(world.query('position')) - len(world.query('position', 'velocity'))}")

def cmd_bench(args):
    n = int(args[0]) if args else 10000
    world = World()
    import time
    t0 = time.perf_counter()
    for i in range(n):
        world.spawn(
            position={'x': i, 'y': i * 0.5},
            velocity={'x': 1, 'y': -1},
            health={'hp': 100, 'max_hp': 100}
        )
    t_spawn = time.perf_counter() - t0

    def move(w, dt):
        for eid, c in w.query('position', 'velocity'):
            c['position']['x'] += c['velocity']['x'] * dt
            c['position']['y'] += c['velocity']['y'] * dt

    world.add_system(move)
    t0 = time.perf_counter()
    for _ in range(10):
        world.tick(1.0)
    t_tick = time.perf_counter() - t0

    t0 = time.perf_counter()
    results = world.query('position', 'health')
    t_query = time.perf_counter() - t0

    print(f"Entities: {n}")
    print(f"Spawn:    {t_spawn:.4f}s ({n/t_spawn:,.0f} entities/s)")
    print(f"10 ticks: {t_tick:.4f}s ({n*10/t_tick:,.0f} updates/s)")
    print(f"Query:    {t_query:.6f}s ({len(results)} results)")

CMDS = {
    'demo': (cmd_demo, '— game world simulation demo'),
    'bench': (cmd_bench, '[N] — benchmark (default 10000 entities)'),
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print("Usage: ecs <command> [args...]")
        for n, (_, d) in sorted(CMDS.items()):
            print(f"  {n:6s} {d}")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd not in CMDS: print(f"Unknown: {cmd}", file=sys.stderr); sys.exit(1)
    CMDS[cmd][0](sys.argv[2:])

if __name__ == '__main__':
    main()
