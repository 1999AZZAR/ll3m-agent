import bpy
import bmesh
import math

def ensure_bmesh(obj=None):
    """Returns a new BMesh or one from the active object."""
    bm = bmesh.new()
    if obj:
        bm.from_mesh(obj.data)
    return bm

def finish_bmesh(bm, obj):
    """Writes BMesh back to object and frees it."""
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

def apply_subd(obj, levels=2):
    """Adds a Subdivision Surface modifier."""
    mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = levels + 1
    return mod

def setup_pbr(name, color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, clearcoat=0.0):
    """Creates a high-fidelity PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    # Generic attribute access for version compatibility
    bsdf.inputs[0].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    try:
        bsdf.inputs['Coat Weight'].default_value = clearcoat
    except:
        try: bsdf.inputs['Clearcoat'].default_value = clearcoat
        except: pass
        
    return mat

def set_smooth(obj, auto_smooth=True):
    """Sets object to shade smooth with auto-smooth enabled."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    if auto_smooth:
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
        else:
            # Blender 4.1+ uses Smooth by Angle modifier
            bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', asset_identifier='Smooth by Angle')

# --- Advanced 2026 Automation Helpers ---

def create_procedural_system(name="ProceduralSystem"):
    """
    Initializes a Geometry Node Tree programmatically for Logic-First modeling.
    Returns the tree, input node, and output node.
    """
    gn_tree = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    nodes = gn_tree.nodes
    in_node = nodes.new('NodeGroupInput')
    in_node.location = (-200, 0)
    out_node = nodes.new('NodeGroupOutput')
    out_node.location = (200, 0)
    
    # Setup default Geometry I/O interface
    gn_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    gn_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    return gn_tree, in_node, out_node

def auto_bake_textures(obj, bake_type='COMBINED', width=2048, height=2048):
    """
    Automates Cycles baking workflow for a given object using the modern 2026 API.
    Returns the baked image path.
    """
    scene = bpy.context.scene
    orig_engine = scene.render.engine
    scene.render.engine = 'CYCLES'
    
    if obj.type != 'MESH':
        return {"error": "Object must be a mesh."}
        
    image_name = f"{obj.name}_Baked_{bake_type}"
    if image_name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[image_name])
    img = bpy.data.images.new(image_name, width=width, height=height)

    # Setup temporary bake nodes
    bake_nodes = []
    for mat in obj.data.materials:
        if not mat or not mat.use_nodes: continue
        nodes = mat.node_tree.nodes
        for node in nodes:
            if node.name == "TEMP_BAKE_NODE": nodes.remove(node)
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.name = "TEMP_BAKE_NODE"
        bake_node.image = img
        bake_node.select = True
        nodes.active = bake_node
        bake_nodes.append((mat, bake_node))

    # Configure Bake
    scene.render.bake.use_clear = True
    scene.render.bake.margin = 16
    scene.render.bake.target = 'IMAGE_TEXTURES'
    
    # Modern context override execution
    try:
        with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
            bpy.ops.object.bake(type=bake_type)
        
        # Save output
        out_path = bpy.path.abspath(f"//_{image_name}.png")
        img.filepath_raw = out_path
        img.file_format = 'PNG'
        img.save()
        status = {"status": "success", "path": out_path}
    except Exception as e:
        status = {"status": "error", "message": str(e)}
    finally:
        # Cleanup
        for mat, node in bake_nodes:
            mat.node_tree.nodes.remove(node)
        scene.render.engine = orig_engine
        
    return status

_hud_handle = None

def draw_agent_hud(message="LL3M Agent Active", color=(0.0, 1.0, 0.8, 1.0)):
    """
    Draws a custom overlay in the 3D viewport using the modern gpu module.
    """
    import gpu
    import blf
    
    global _hud_handle
    if _hud_handle:
        bpy.types.SpaceView3D.draw_handler_remove(_hud_handle, 'WINDOW')
        _hud_handle = None
        
    if not message:
        return # Used to clear HUD
        
    def draw():
        font_id = 0
        blf.position(font_id, 20, 20, 0)
        blf.size(font_id, 24)
        blf.color(font_id, *color)
        blf.draw(font_id, message)
        
    _hud_handle = bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')
    
    # Force redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
