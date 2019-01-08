# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Math Mesh",
    "author": "Ryan Southall",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Mesh",
    "wiki_url": "https://blendscript.blogspot.com/2019/01/blender-28-math-mesh.html",
    "tracker_url": "https://github.com/rgsouthall/math_mesh/issues"}


import bpy, bmesh
from mathutils import Vector
from math import pi, sin

def ret_curve(ct, alt, ang, power):
    if ct == '0' and alt:
        y = sin(ang)
    
    elif ct == '0' and not alt:
        y = abs(sin(ang))
    
    elif ct == '1':
        odd = 1 if int(2 * ang/(2*pi))%2 else 0
        ang = abs(2 * ang - int(2 * ang/(2*pi)) * 2 * pi)
        y = -((pi**2 - (pi - ang)**2)/pi**2)**0.5 if odd else ((pi**2 - (pi - ang)**2)/pi**2)**0.5
        
    if not alt:
        y = abs(y)

    if power != 1:
        y = (1 + y)**power - 1 if y > 0 else -1 * ((1 - y)**power - 1)
        
    return y
       
class MESH_OT_math_mesh(bpy.types.Operator):
    """Create a mathematical mesh curve"""
    bl_idname = "mesh.math_mesh"
    bl_label = "Math Mesh"
    bl_options = {'REGISTER', 'UNDO'}

# Colons now required in 2.8 as properties are now fields
    ctype: bpy.props.EnumProperty(
            items=[("0", "Sine", "Sine curve"),
                   ("1", "Circular", "Semi-circular curve")],
            name="Curve type",
            description="Specify the curve type",
            default="0")
    
    plane: bpy.props.EnumProperty(
            items=[("0", "XY", "Plane the curve drawn on"),
                   ("1", "XZ", "Plane the curve drawn on"),
                   ("2", "YZ", "Plane the curve drawn on"),
                   ("3", "View", "Plane the curve drawn on")],
            name="Curve plane",
            description="Specify the plane the curve is drawn on",
            default="0")
    
    cn: bpy.props.IntProperty(name="No. of curves",
            description="Specifiy the number of oscillations",
            default=5, min = 1)
    
    vn: bpy.props.IntProperty(name="Curve vertices",
            description="Specify the number of vertices per curve",
            default=10, min = 1)   
    
    atype: bpy.props.EnumProperty(
            items=[("0", "Absolute", "Absolute amplitude value"),
                   ("1", "Relative", "Relative anplitude value")],
            name="Amplitude type",
            description="Specify the amplitude type",
            default="1")
    
    amp: bpy.props.FloatProperty(name="Amplitude", description="Specify the amplitude of the curve", default = 1)
    
    power: bpy.props.FloatProperty(name="Power", description="Apply a power to the curve values", default = 1, min = 0.1, max = 10)
    
    skew: bpy.props.FloatProperty(name="Skew", description="Apply a skew to the curve values", default = 0)
    
    alternate: bpy.props.BoolProperty(name="Alternate:", default = 1)
    
    def execute(self, context):
        self.bmesh = bmesh.from_edit_mesh(context.active_object.data)
        self.bmverts = [v for v in self.bmesh.verts if v.select]
        
        if not len(self.bmverts) == 2:
            self.report({'ERROR'}, 'Two vertices must be selected')
            return {'CANCELLED'}

        pvector = (Vector((0, 0, 1)), Vector((0, 1, 0)), Vector((1, 0, 0)), context.space_data.region_3d.view_rotation@Vector((0.0, 0.0, -1.0)))[int(self.plane)]        
        vector = self.bmverts[1].co - self.bmverts[0].co
        distance = vector.length
        t_angle = pi * self.cn
        t_verts = self.cn * self.vn
        uvector = vector.cross((pvector)).normalized()
        lastv = self.bmverts[0].co
        vis = [self.bmverts[0]]        
        samp = self.amp * distance/(self.cn * 2) if self.ctype == '1' else self.amp * distance/(self.cn * pi)        
        amp = samp if self.atype == '1' else self.amp
                    
        for i in range(1, t_verts):
            y = ret_curve(self.ctype, self.alternate, i/t_verts * t_angle, self.power)
            vis.append(self.bmesh.verts.new(lastv + i/t_verts * vector + y * vector.normalized() * self.skew + y * uvector * amp))        
        vis.append(self.bmverts[1])

        for vi in range(0, len(vis) - 1):
            self.bmesh.edges.new([vis[vi], vis[vi + 1]]).select = True
                   
        bmesh.update_edit_mesh(context.active_object.data)    
        context.active_object.data.update()
        return {'FINISHED'}

addon_keymaps = []
classes = (MESH_OT_math_mesh,)

def register():
    for cl in classes:
        bpy.utils.register_class(cl)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    km.keymap_items.new("mesh.math_mesh", 'M', 'PRESS', alt=True, shift=True)
    addon_keymaps.append(km)

def unregister():
    for cl in classes:
        bpy.utils.unregister_class(cl)
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]


