# Pattern: Subdivision Surface (SubD) Topology

Create low-poly quad-based meshes for the Subsurf modifier.

## SubD Base Setup
```python
subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3
```

## Support Loops
To maintain sharp edges while using SubD, use `Mean Crease`:
```python
bm = bmesh.new()
# ... build geometry
crease_layer = bm.edges.layers.crease.verify()
for e in bm.edges:
    if e.is_boundary:
        e[crease_layer] = 1.0 # Sharp edge
```
