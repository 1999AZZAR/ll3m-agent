# Pattern: Ergonomic Curves (Taper/Sweep)

For handles and surfaces, use vertex coordinate manipulation in `bmesh`.

## Tapering Logic
```python
def taper_object(obj, factor=0.5):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        if v.co.z < 0: # Bottom
            v.co.x *= factor
            v.co.y *= factor
    bm.to_mesh(obj.data)
    bm.free()
```

## Smoothing
```python
bpy.ops.object.shade_smooth()
obj.data.use_auto_smooth = True
```
