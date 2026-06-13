# Pattern: Realistic PBR Materials

Use the Principled BSDF with realistic secondary inputs.

## Clearcoat (Lacquered Finish)
```python
bsdf.inputs['Coat Weight'].default_value = 1.0
bsdf.inputs['Coat Roughness'].default_value = 0.05
```

## Sheen (Fabric/Cloth)
```python
bsdf.inputs['Sheen Weight'].default_value = 0.5
bsdf.inputs['Sheen Roughness'].default_value = 0.2
```

## Metallic Anisotropy
```python
bsdf.inputs['Anisotropic'].default_value = 0.5
bsdf.inputs['Anisotropic Rotation'].default_value = 0.25
```
