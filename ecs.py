#!/usr/bin/env python3
"""Entity Component System framework."""
import sys
class World:
    def __init__(self): self.next_id=0; self.components={}; self.systems=[]
    def spawn(self,**comps):
        eid=self.next_id; self.next_id+=1
        for k,v in comps.items(): self.components.setdefault(k,{})[eid]=v
        return eid
    def get(self,eid,comp): return self.components.get(comp,{}).get(eid)
    def query(self,*comps):
        if not comps: return []
        ids=set(self.components.get(comps[0],{}).keys())
        for c in comps[1:]: ids&=set(self.components.get(c,{}).keys())
        return [(eid,{c:self.components[c][eid] for c in comps}) for eid in ids]
    def add_system(self,fn): self.systems.append(fn)
    def tick(self):
        for s in self.systems: s(self)
w=World()
w.spawn(pos=[0,0],vel=[1,2],name="player")
w.spawn(pos=[5,5],vel=[-1,0],name="enemy")
w.spawn(pos=[3,3],name="wall")
def move(world):
    for eid,c in world.query('pos','vel'):
        c['pos'][0]+=c['vel'][0]; c['pos'][1]+=c['vel'][1]
def display(world):
    for eid,c in world.query('pos','name'):
        print(f"  {c['name']}: pos={c['pos']}")
w.add_system(move); w.add_system(display)
for t in range(3): print(f"Tick {t}:"); w.tick()
