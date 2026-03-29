#!/usr/bin/env python3
"""Entity Component System for game/simulation architecture."""
import sys
from collections import defaultdict

class World:
    def __init__(self):
        self._next_id = 0
        self.components = defaultdict(dict)  # comp_type -> {entity_id: data}
        self.entities = set()
    def create_entity(self):
        eid = self._next_id; self._next_id += 1
        self.entities.add(eid)
        return eid
    def destroy_entity(self, eid):
        self.entities.discard(eid)
        for store in self.components.values():
            store.pop(eid, None)
    def add_component(self, eid, comp_type, data):
        self.components[comp_type][eid] = data
    def get_component(self, eid, comp_type):
        return self.components[comp_type].get(eid)
    def has_component(self, eid, comp_type):
        return eid in self.components.get(comp_type, {})
    def query(self, *comp_types):
        if not comp_types: return []
        sets = [set(self.components.get(ct, {}).keys()) for ct in comp_types]
        common = sets[0]
        for s in sets[1:]: common &= s
        return [(eid, tuple(self.components[ct][eid] for ct in comp_types)) for eid in common]

def test():
    w = World()
    e1 = w.create_entity()
    e2 = w.create_entity()
    w.add_component(e1, "pos", {"x": 0, "y": 0})
    w.add_component(e1, "vel", {"dx": 1, "dy": 2})
    w.add_component(e2, "pos", {"x": 5, "y": 5})
    movers = w.query("pos", "vel")
    assert len(movers) == 1 and movers[0][0] == e1
    assert w.get_component(e2, "pos")["x"] == 5
    assert not w.has_component(e2, "vel")
    w.destroy_entity(e1)
    assert len(w.query("pos")) == 1
    print("  ecs: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Entity Component System")
