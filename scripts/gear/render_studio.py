"""Open the exported R7 setup in a lit, editable Blender studio and render a reference frame."""
import bpy,os,math,sys
from mathutils import Matrix,Vector
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
OUT=os.path.join(ROOT,'output/gear-modeling')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
body_only='--body-only' in sys.argv
body_id=next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--body=')),'r7')
if body_id not in ['r7','40d','c200']:raise ValueError('Unknown body audit target')
parts=[(body_id,0)] if body_only else [(body_id,0),('adapter',.53),('28-135',.53-.088+24/55)] if body_id=='r7' else [(body_id,0),('28-135',.53-.088)]
for part,z in parts:
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,'output/gear-modeling/uncompressed',part+'.glb'))
    imported=list(bpy.context.selected_objects)
    root=bpy.data.objects.new(part,None);bpy.context.collection.objects.link(root)
    for obj in imported:
        if obj.parent is None:obj.parent=root
    root.rotation_euler.x=-math.pi/2;root.location.z=z
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.use_nodes=True;nodes=scene.world.node_tree.nodes;links=scene.world.node_tree.links
hdr=nodes.new('ShaderNodeTexEnvironment');hdr.image=bpy.data.images.load(os.path.join(ROOT,'public/models/gear/studio.hdr'));links.new(hdr.outputs['Color'],nodes.get('Background').inputs['Color']);nodes.get('Background').inputs['Strength'].default_value=.4
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for n in list(mat.node_tree.nodes):
        if n.type=='TEX_IMAGE' and n.image and ('normal' in n.image.name.lower() or (any(name in mat.name for name in ['Pebbled rubber','Scanned grip rubber']) and 'roughness' in n.image.name.lower())):
            grain=1.25 if 'Scanned grip rubber' in mat.name else 6 if 'Crinkle painted metal' in mat.name else 3 if 'Pebbled rubber' in mat.name else 5
            uv=mat.node_tree.nodes.new('ShaderNodeTexCoord');mapping=mat.node_tree.nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(grain,grain,grain);mat.node_tree.links.new(uv.outputs['UV'],mapping.inputs['Vector']);mat.node_tree.links.new(mapping.outputs['Vector'],n.inputs['Vector'])
        if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value*=.8 if any(name in mat.name for name in ['Pebbled rubber','Scanned grip rubber']) else .6

def aim(o,target):
    forward=(Vector(target)-o.location).normalized();hint=Vector((0,0,1)) if abs(forward.y)>.99 else Vector((0,1,0));right=forward.cross(hint).normalized();up=right.cross(forward)
    o.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
for name,loc,power,size,color in [('Key',(-3,5,4),450,4,(1,.96,.9)),('Edge',(4,3,-3),550,3,(.8,.9,1)),('Front',(-2,1,5),100,2,(1,1,1))]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,.7))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,-.94,0),rotation=(math.pi/2,0,0));floor=bpy.context.object;floor.name='Charcoal studio floor';mat=bpy.data.materials.new('Charcoal');mat.diffuse_color=(.008,.008,.008,1);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.008,.008,.008,1);p.inputs['Roughness'].default_value=.5;floor.data.materials.append(mat)
data=bpy.data.cameras.new('Product camera');cam=bpy.data.objects.new('Product camera',data);scene.collection.objects.link(cam);cam.location=(-4.8,2.6,7.8);aim(cam,(-.1,.0,.85));data.lens=55;scene.camera=cam
scene.view_settings.view_transform='AgX';scene.render.filepath=os.path.join(OUT,'r7-studio.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,body_id+'-body-studio.blend' if body_only else 'camera-loadout-studio.blend'))
if '--audit' in sys.argv:
    scene.render.resolution_x=1100;scene.render.resolution_y=850
    scene.cycles.samples=32
    views=[('front',(0,.15,8),(0,.05,.7)),('rear',(-.1,.15,-7),(-.1,.05,0)),('side',(-8,.2,1),(-.1,.0,1))]
    if body_only:views=[('front',(-.2,.05,8),(-.2,.05,0)),('rear',(-.2,.05,-8),(-.2,.05,0)),('side',(-8,0,.1),(0,0,.1)),('top',(-.2,8,.1),(-.2,0,.1)),('bottom',(-.2,-8,.1),(-.2,0,.1))]
    if body_id=='c200':
        floor.location.y=-1.36
        views=[('front',(0,1.10,8),(0,1.10,-.5)),('rear',(0,1.10,-8),(0,1.10,-.5)),('side',(8,1.10,-.6),(0,1.10,-.6)),('grip',(-8,1.10,-.6),(0,1.10,-.6)),('top',(0,8,-.6),(0,0,-.6))]
    for name,position,target in views:
        floor.hide_render=name=='bottom'
        cam.location=position;aim(cam,target);cam.data.type='ORTHO';cam.data.ortho_scale=8 if body_id=='c200' else 3.9
        scene.render.filepath=os.path.join(OUT,('audit-'+body_id+'-body-' if body_only else 'audit-')+name+'.png');bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(write_still=True)
