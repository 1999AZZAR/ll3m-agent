# Pattern: Realistic Rounded Corners

Instead of sharp $90^\circ$ edges, use Bevel modifiers or BMesh beveling to catch light.

## BMesh Implementation
```python
import bmesh
def bevel_edges(obj, width=0.01):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    edges = [e for e in bm.edges]
    bmesh.ops.bevel(bm, geom=edges, offset=width, segments=3, profile=0.5)
    bm.to_mesh(obj.data)
    bm.free()
```

## Modifier Implementation
```python
bev = obj.modifiers.new(name="Bevel", type='BEVEL')
bev.width = 0.01
bev.segments = 3
```
