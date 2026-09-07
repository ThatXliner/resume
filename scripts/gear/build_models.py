"""Build reference-driven camera assets. Run with Blender --background --python.
Geometry is authored in the viewer's Y-up coordinates; export_yup=False preserves them.
See REFERENCES.md for the product references used to model each object.
"""
import bpy, math, os, sys, json
import numpy as np
from mathutils import Vector, Matrix
from math import sin, cos, pi
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
OUT=os.path.join(ROOT,'public/models/gear')
WORK=os.path.join(ROOT,'output/gear-modeling')
os.makedirs(OUT,exist_ok=True);os.makedirs(WORK,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
M={}; OBJECTS=[]; current=''; fonts={}

def image(name,data):
    h,w=data.shape[:2];rgba=np.ones((h,w,4),np.float32);rgba[:,:,:3]=data[:,:,:3]
    img=bpy.data.images.new(name,width=w,height=h,alpha=False)
    img.pixels.foreach_set(rgba.reshape(-1));img.filepath_raw=os.path.join(WORK,name+'.png');img.file_format='PNG';img.save();img.pack();return img

def surface_maps():
    n=512;rng=np.random.default_rng(2026)
    yy,xx=np.mgrid[:n,:n].astype(float);gx=xx/n*48;gy=yy/n*48
    seeds=rng.random((48,48,2));dist=np.ones((n,n))*100
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            ix=np.floor(gx).astype(int)+dx;iy=np.floor(gy).astype(int)+dy
            sx=ix+seeds[iy%48,ix%48,0];sy=iy+seeds[iy%48,ix%48,1]
            dist=np.minimum(dist,(gx-sx)**2+(gy-sy)**2)
    height=np.exp(-dist*3.8)*.7+rng.random((n,n))*.09
    def normal(h,strength):
        nx=(np.roll(h,-1,axis=1)-np.roll(h,1,axis=1))*strength
        ny=(np.roll(h,-1,axis=0)-np.roll(h,1,axis=0))*strength
        nz=np.ones_like(nx);vec=np.stack([-nx,-ny,nz],axis=-1);vec/=np.linalg.norm(vec,axis=-1)[...,None];return vec*.5+.5
    pebble=image('rubber-pebble-normal',normal(height,2.8))
    fine=image('magnesium-normal',normal(rng.random((n,n))*.17,1.3))
    return pebble,fine
PEBBLE,FINE=surface_maps()
LEATHER=bpy.data.images.load(os.path.join(ROOT,'scripts/gear/textures/Leather037_NormalGL.png'));LEATHER.colorspace_settings.name='Non-Color';LEATHER.pack()
leather_rough_source=bpy.data.images.load(os.path.join(ROOT,'scripts/gear/textures/Leather037_Roughness.png'));leather_rough_source.colorspace_settings.name='Non-Color'
leather_values=np.array(leather_rough_source.pixels[:],dtype=np.float32).reshape(leather_rough_source.size[1],leather_rough_source.size[0],4)[:,:,:3]
LEATHER_ROUGH=image('camera-grip-roughness',.52+.35*leather_values);LEATHER_ROUGH.colorspace_settings.name='Non-Color'

def material(name,color,rough=.4,metal=0,normal=None,normal_strength=.45,transmission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if transmission:p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.48;p.inputs['Coat Weight'].default_value=.3
    if normal:
        tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=normal;tex.image.colorspace_settings.name='Non-Color'
        nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=normal_strength;m.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
        # Small finish variation breaks up a uniform specular response without
        # adding fake wear. Scalar texture values are linear material data.
        rng=np.random.default_rng(sum(ord(c) for c in name))
        field=rng.random((128,128))
        for _ in range(3):field=(field+np.roll(field,1,0)+np.roll(field,-1,0)+np.roll(field,1,1)+np.roll(field,-1,1))/5
        field=(field-field.mean())/(field.std()+1e-6)
        values=np.clip(rough+field*(.035 if normal==PEBBLE else .018),.05,.95)
        rough_img=image(name.lower().replace(' ','-')+'-roughness',np.repeat(values[:,:,None],3,axis=2))
        rough_img.colorspace_settings.name='Non-Color'
        rough_tex=m.node_tree.nodes.new('ShaderNodeTexImage');rough_tex.image=rough_img
        if normal==LEATHER:rough_tex.image=LEATHER_ROUGH
        m.node_tree.links.new(rough_tex.outputs['Color'],p.inputs['Roughness'])
    M[name]=m;return m
material('Graphite polymer',(.013,.014,.016),.52,0,FINE,.4)
material('Magnesium shell',(.018,.019,.021),.55,0,FINE,.35)
material('Pebbled rubber',(.009,.0095,.01),.66,0,LEATHER,3.0)
M['Pebbled rubber'].name='Scanned grip rubber'
material('Crinkle painted metal',(.010,.011,.013),.48,0,PEBBLE,.48)
material('Focus rubber',(.011,.011,.012),.56,0,FINE,.35)
material('Blackened aperture steel',(.006,.007,.008),.42,.35)
material('Eyepiece optical glass',(.008,.007,.012),.028,0)
material('Anodized black',(.009,.01,.011),.28,.55)
material('Deep black',(.002,.0024,.003),.55,0)
material('Optical barrel flocking',(.003,.0035,.004),.84,0)
material('Machined optical baffles',(.009,.010,.011),.57,0,FINE,.18)
M['Optical barrel flocking'].node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.05
# Fine annular machining changes finish without subpixel mesh edges.
vr=np.linspace(0,1,512)[:,None];rough=np.full((512,16),.84)
for center in np.linspace(.104,.634,6):rough-=.12*np.exp(-((vr-center)/.008)**2)
baffle_map=image('optical-baffle-roughness',np.repeat(rough[:,:,None],3,axis=2));baffle_map.colorspace_settings.name='Non-Color'
baffle_nodes=M['Optical barrel flocking'].node_tree
baffle_tex=baffle_nodes.nodes.new('ShaderNodeTexImage');baffle_tex.image=baffle_map
baffle_nodes.links.new(baffle_tex.outputs['Color'],baffle_nodes.nodes.get('Principled BSDF').inputs['Roughness'])

material('Machined metal',(.45,.47,.48),.25,.85)
material('Screw steel',(.09,.1,.11),.28,.85)
material('White enamel',(.66,.645,.59),.34,0,FINE,.16)
material('Red lacquer',(.46,.018,.011),.27,.15)
material('Gold engraving',(.48,.35,.12),.4,.45)
material('White ink',(.76,.78,.74),.5,0)
material('Blue ink',(.065,.36,.66),.4,0)
material('Green ink',(.07,.53,.25),.45,0)
material('LCD glass',(.009,.017,.02),.1,.22)
# Opaque display stack under cover glass: a black dielectric, not tinted metal.
material('Inactive display glass',(.0025,.003,.0032),.075,0)
material('LCD display',(.075,.095,.068),.28,0)
material('Inactive LCD segments',(.040,.056,.038),.34,0)
material('Sensor filter edge',(.018,.04,.09),.17,.3)
material('Sensor coating',(.004,.018,.013),.065,.25)
material('Reflex mirror',(.62,.64,.63),.045,1)
material('Optical glass',(.88,.98,.94),.045,0,transmission=1)
material('Inner optical glass',(.65,.78,.95),.07,0,transmission=.94)

def register(o,name,mat):
    o.name=current+' / '+name
    if mat:o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    OBJECTS.append(o);return o

def active(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def apply(o,mod):
    active(o);bpy.ops.object.modifier_apply(modifier=mod.name)

def finish(o,bevel=0,segments=3,smooth=True):
    if bevel:
        mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=segments;apply(o,mod)
    if smooth:
        for p in o.data.polygons:p.use_smooth=True
        mod=o.modifiers.new('Surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40;apply(o,mod)
    return o

def box(name,p,size,mat='Graphite polymer',bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=register(bpy.context.object,name,mat);o.scale=size;active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,bevel)

def cyl(name,p,r,length,mat='Anodized black',axis='z',vertices=96,bevel=.006):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=length,location=p);o=register(bpy.context.object,name,mat)
    if axis=='y':o.rotation_euler.x=pi/2
    if axis=='x':o.rotation_euler.y=pi/2
    return finish(o,bevel,2)

def ring(name,z,outer,inner,depth,mat='Anodized black',center=(0,0),segments=128):
    verts=[];faces=[]
    for radius,zz in [(outer,z-depth/2),(outer,z+depth/2),(inner,z+depth/2),(inner,z-depth/2)]:
        verts.extend([(center[0]+radius*cos(i*2*pi/segments),center[1]+radius*sin(i*2*pi/segments),zz) for i in range(segments)])
    for row in range(4):
        for i in range(segments):j=(i+1)%segments;faces.append((row*segments+i,row*segments+j,((row+1)%4)*segments+j,((row+1)%4)*segments+i))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat);finish(o,.0025,2);return o

def sphere(name,p,size,mat='Graphite polymer'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=p);o=register(bpy.context.object,name,mat);o.scale=size;active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for poly in o.data.polygons:poly.use_smooth=True
    return o

def optical_element(name,z,r,sag=.025,thickness=.035,mat='Optical glass'):
    # Closed, shallow biconvex element. Scaling a sphere flattens its center but
    # retains near-vertical edge normals, distorting the entire barrel reflection.
    segments=128;rows=16;verts=[];faces=[];surface=[]
    for side in [1,-1]:
        center=len(verts);verts.append((0,0,z+side*(thickness/2+sag)))
        rings=[]
        for j in range(1,rows+1):
            t=j/rows;rr=r*t;zz=z+side*(thickness/2+sag*(1-t*t));start=len(verts);rings.append(start)
            verts.extend((rr*cos(i*2*pi/segments),rr*sin(i*2*pi/segments),zz) for i in range(segments))
            for i in range(segments):
                nxt=(i+1)%segments
                if j==1:faces.append((center,start+i,start+nxt))
                else:faces.append((rings[-2]+i,start+i,start+nxt,rings[-2]+nxt))
        surface.append(rings[-1])
    for i in range(segments):
        nxt=(i+1)%segments;faces.append((surface[0]+i,surface[1]+i,surface[1]+nxt,surface[0]+nxt))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat)
    for p in mesh.polygons:p.use_smooth=True
    return o

def eyecup(x,y,z,body='c200'):
    # Four rounded rectangular loops form a hollow rubber hood. The glass sits
    # behind its opening, rather than on top of a solid block.
    box('Eyecup mounting seat',(x,y,z+.035),(.77,.43,.05),'Graphite polymer',.045)
    verts=[];faces=[];steps=12;n=4*(steps+1)
    loops=[(.76,.43,.12,.02),(.84,.48,.14,-.145),(.49,.31,.065,-.151),(.40,.26,.045,.015)]
    if body=='r7':
        loops=[(.76,.46,.13,.02),(.83,.51,.15,-.145),(.66,.39,.10,-.151),(.60,.34,.075,-.035)]
    elif body=='40d':
        loops=[(.79,.48,.13,.02),(.87,.55,.16,-.125),(.64,.40,.09,-.137),(.59,.36,.07,-.04)]
    elif body=='c200':
        loops=[(.78,.57,.16,.02),(.87,.66,.18,-.16),(.69,.48,.10,-.175),(.61,.41,.07,-.025)]
    for w,h,r,depth in loops:
        for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,pi/2),(-w/2+r,-h/2+r,pi),(w/2-r,-h/2+r,pi*1.5)]:
            for i in range(steps+1):
                a=start+i*pi/2/steps;verts.append((x+cx+r*cos(a),y+cy+r*sin(a),z+depth))
    for j in range(4):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i))
    mesh=bpy.data.meshes.new('Hollow eyecup');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Eyecup',mesh);scene.collection.objects.link(o);register(o,'Hollow molded eyecup','Focus rubber');finish(o,.012,3)
    # Separate optical carrier inside the rubber cup; the DSLR has no eye sensor.
    box('Eyepiece inner carrier',(x,y,z-.045),(.65,.44,.034) if body=='c200' else (.59,.35,.034),'Graphite polymer',.038)
    optical_x=x+.035 if body=='r7' else x-.045 if body=='c200' else x
    box('Eyepiece optical recess',(optical_x,y,z-.066),(.43,.38,.016) if body=='c200' else (.365,.275,.016),'Deep black',.029)
    # A shallow convex optical face catches reflections across its curved surface.
    sag=.022 if body=='c200' else .029 if body=='r7' else .024
    vertices=[(optical_x,y,z-.078-sag)];polygons=[];count=52 if body=='c200' else 100;rows=8 if body=='c200' else 32
    def optic_vertex(dx,dy,t):
        depth=z-.078-sag*(1-t*t)
        if body!='c200':
            # A rectangular cut from a spherical lens, with a smooth analytic
            # surface rather than rounded rectangular iso-depth rings.
            radius=(.155**2+.110**2+sag**2)/(2*sag)
            depth=z-.078-sag+radius-math.sqrt(radius*radius-dx*dx-dy*dy)
        vertices.append((optical_x+dx,y+dy,depth))
    for row in range(1,rows+1):
        t=row/rows;w=(.38 if body=='c200' else .31)*t;h=(.33 if body=='c200' else .22)*t;r=.033*t;start_index=len(vertices)
        corners=[(w/2-r,h/2-r,0),(-w/2+r,h/2-r,pi/2),(-w/2+r,-h/2+r,pi),(w/2-r,-h/2+r,pi*1.5)]
        for corner,(cx,cy,angle) in enumerate(corners):
            for i in range(13):
                a=angle+i*pi/24
                optic_vertex(cx+r*cos(a),cy+r*sin(a),t)
            if body!='c200':
                # Sample the straight edges too; corner-only sampling leaves
                # broad flat strips that break up the polished reflection.
                end=(cx+r*cos(angle+pi/2),cy+r*sin(angle+pi/2))
                nx,ny,na=corners[(corner+1)%4];following=(nx+r*cos(na),ny+r*sin(na))
                for j in range(1,13):
                    u=j/13;optic_vertex(end[0]*(1-u)+following[0]*u,end[1]*(1-u)+following[1]*u,t)
        for i in range(count):
            j=(i+1)%count
            if row==1:polygons.append((0,start_index+j,start_index+i))
            else:polygons.append((start_index-count+i,start_index-count+j,start_index+j,start_index+i))
    mesh=bpy.data.meshes.new('Rectangular curved eyepiece optic');mesh.from_pydata(vertices,[],polygons);mesh.update()
    optic=bpy.data.objects.new('Eyepiece optic',mesh);scene.collection.objects.link(optic);register(optic,'Rectangular curved eyepiece optic','LCD glass' if body=='c200' else 'Eyepiece optical glass')
    for face in mesh.polygons:face.use_smooth=True
    if body=='c200':
        box('C200 eye sensor bezel',(x+.244,y,z-.067),(.074,.169,.018),'Deep black',.013)
        box('C200 eye sensor window',(x+.244,y,z-.079),(.046,.136,.006),'Sensor coating',.009)
        return
    if body=='r7':
        box('Viewfinder proximity sensor bezel',(x-.237,y,z-.065),(.091,.139,.016),'Deep black',.016)
        box('Viewfinder proximity sensor window',(x-.237,y,z-.076),(.063,.110,.006),'Sensor coating',.013)
    else:
        box('Eyecup retaining lower rail',(x,y-.207,z-.060),(.47,.034,.030),'Anodized black',.006)
    # Diopter wheel sits on the right side of the finder when viewed from behind.
    dx=x-.405;dy=y+.145;dz=z+.025
    cyl('Diopter axle',(dx,dy,dz),.104,.079,'Deep black','x',64,.004)
    cyl('Diopter adjustment wheel',(dx-.017,dy,dz),.093,.088,'Graphite polymer','x',64,.004)
    for i in range(36):
        a=2*pi*i/36
        tooth=box('Diopter wheel knurl',(dx-.017,dy+.093*cos(a),dz+.093*sin(a)),(.086,.010,.010),'Focus rubber',.002)
        tooth.rotation_euler.x=a

def text(name,words,p,size=.08,mat='White ink',rotation=(0,0,0),font='Arial',align='CENTER'):
    if words=='Canon' and font=='Canon':
        paths=json.load(open(os.path.join(ROOT,'scripts/gear/canon-contours.json')))
        curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH';curve.resolution_u=2
        for path in paths:
            sp=curve.splines.new('POLY');sp.points.add(len(path)-1);sp.use_cyclic_u=True
            for point,(x,y) in zip(sp.points,path):point.co=(x*size*3.65,y*size*3.65,0,1)
        o=bpy.data.objects.new(name,curve);scene.collection.objects.link(o);o.location=p;o.rotation_euler=rotation;register(o,name,mat);active(o);bpy.ops.object.convert(target='MESH');return o
    if font not in fonts:
        file={'Arial':'Arial.ttf','Bold':'Arial Bold.ttf','Canon':'Georgia Bold.ttf'}[font]
        fonts[font]=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/'+file)
    curve=bpy.data.curves.new(name,'FONT');curve.body=words;curve.size=size;curve.align_x=align;curve.align_y='CENTER';curve.font=fonts[font];curve.resolution_u=6
    o=bpy.data.objects.new(name,curve);scene.collection.objects.link(o);o.location=p;o.rotation_euler=rotation;register(o,name,mat);active(o);bpy.ops.object.convert(target='MESH');return o

def arc_text(words,z,radius,size=.048,start=None,span=None,mat='White ink',bottom=False):
    if span is None:span=len(words)*size*.59/radius
    if start is None:start=pi/2+span/2
    for i,ch in enumerate(words):
        angle=start-i*span/max(1,len(words)-1)
        text('Front ring inscription',ch,(cos(angle)*radius,sin(angle)*radius,z),size,mat,rotation=(0,0,angle-pi/2))

def line(name,points,radius=.005,mat='Deep black'):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=8;curve.bevel_depth=radius;curve.bevel_resolution=2
    sp=curve.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,curve);scene.collection.objects.link(o);register(o,name,mat);active(o);bpy.ops.object.convert(target='MESH');return o

def screw(p,axis='z',r=.026):
    cyl('Recessed cross-head screw',p,r,.009,'Screw steel',axis,32,.003)
    for angle in [0,pi/2]:
        b=box('Screw slot',(p[0],p[1],p[2]+.006),(r*1.1,.005,.002),'Deep black',.001);b.rotation_euler.z=angle
        if axis=='x':
            b.location=(p[0]-.006,p[1],p[2]);b.rotation_euler.y=-pi/2
            if angle:b.rotation_euler.x=angle

def smooth_outline(points,steps=6):
    # Round each corner without spline overshoot at the long bottom edge.
    out=[]
    for i,point in enumerate(points):
        p=np.array(point,float);before=np.array(points[(i-1)%len(points)],float);after=np.array(points[(i+1)%len(points)],float)
        left=before-p;right=after-p
        a=p+left/np.linalg.norm(left)*min(.10,np.linalg.norm(left)*.4)
        b=p+right/np.linalg.norm(right)*min(.10,np.linalg.norm(right)*.4)
        for j in range(steps+1):
            t=j/steps;out.append((1-t)**2*a+2*(1-t)*t*p+t*t*b)
    return out

def profile(name,points,back,front,mat='Magnesium shell',bevel=.035):
    # Boolean cutters require outward-facing solids before export's normal pass.
    # Accept either outline winding without creating an inside-out casting.
    points=list(points)
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))<0:points.reverse()
    points=smooth_outline(points);n=len(points);verts=[(x,y,z) for z in [back,front] for x,y in points];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat);return finish(o,bevel,4)

def loft_grip(name,rows,mat):
    n=64;verts=[];faces=[]
    for y,cx,cz,rx,rz in rows:
        verts.extend([(cx+cos(i*2*pi/n)*rx,y,cz+sin(i*2*pi/n)*rz) for i in range(n)])
    for row in range(len(rows)-1):
        for i in range(n):j=(i+1)%n;faces.append((row*n+i,row*n+j,(row+1)*n+j,(row+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple(range((len(rows)-1)*n,len(rows)*n))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat)
    mod=o.modifiers.new('Sculpted continuous grip','SUBSURF');mod.levels=2;apply(o,mod)
    for p in o.data.polygons:p.use_smooth=True
    return o

def radial_ribs(name,z,r,length,count=120,mat='Focus rubber'):
    # One mesh for all of the fine molded ribs avoids hundreds of draw calls.
    verts=[];faces=[]
    for i in range(count):
        angle=i*2*pi/count;da=pi/count*.35
        for zz in [z-length/2,z+length/2]:
            for rr,aa in [(r,angle-da),(r+.007,angle-da),(r+.007,angle+da),(r,angle+da)]:verts.append((rr*cos(aa),rr*sin(aa),zz))
        k=i*8;faces.extend([tuple(k+j for j in ids) for ids in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat);finish(o,.0018,2);return o

def dial(p,r=.19,axis='y',mode=False,width=.085):
    start=len(OBJECTS);cyl('Control dial rubber', (0,0,0),r,.085,'Focus rubber');radial_ribs('Knurled dial edge',0,r,.063,64)
    cyl('Dial top',(0,0,.047),r*.92,.013,'Anodized black')
    if mode:
        modes=['M','Av','Tv','P','SCN','A+','C3','C2','C1','B'] if mode=='r7' else ['M','Av','Tv','P','AUTO','C3','C2','C1','A-DEP'] if mode=='40d' else ['M','Av','Tv','P','Fv','A+','C1','C2']
        for i,t in enumerate(modes):
            a=i*2*pi/len(modes);text('Mode '+t,t,(cos(a)*r*.72,sin(a)*r*.72,.056),.034 if mode=='r7' else .041,'Green ink' if t=='A+' else 'White ink',rotation=(0,0,a-pi/2))
    else:cyl('Dial center',(0,0,.052),r*.44,.025,'Graphite polymer')
    if width!=.085:
        stretch=Matrix.Diagonal(Vector((1,1,width/.085,1)))
        for o in OBJECTS[start:]:o.matrix_world=stretch@o.matrix_world
    rot=Matrix.Rotation(-pi/2,4,'X') if axis=='y' else Matrix.Rotation(pi,4,'Y') if axis=='rear' else Matrix.Rotation(pi/2,4,'Y') if axis=='x' else Matrix.Identity(4)
    for o in OBJECTS[start:]:o.matrix_world=Matrix.Translation(Vector(p))@rot@o.matrix_world

def mount(z=.48,mirror=False,rf=False,cinema=False):
    ring('Mount casting boss',z-.105,.641,.435,.215,'Graphite polymer')
    ring('Mount gasket',z,.655,.455,.075,'Deep black')
    # The 40D EF seating face is almost covered by the attached rear shoulder.
    # The previous oversized face left a broad silver annulus in side views.
    flange_radius=.591 if mirror else .626
    screw_radius=.555 if mirror else .583
    ring('Stainless lens flange',z+.042,flange_radius,.492,.018,'Machined metal')
    ring('Inner bayonet',z+.047,.5,.435,.028,'Anodized black')
    for a in [pi/4,3*pi/4,5*pi/4,7*pi/4]:screw((cos(a)*screw_radius,sin(a)*screw_radius,z+.055),r=.022)
    cyl('Red mount index',(0,.659,z+.053),.018,.014,'Red lacquer',vertices=24)
    sensor_z=z+.051-20/55 if rf else z+.051-44/55 if cinema else z-.84 if mirror else z-.195
    if cinema:
        # The C200 front reference shows a clipped-corner filter cassette,
        # retaining screws and a blue filter surround inside the EF throat.
        # Keep the actual sensor at EF register depth behind that assembly.
        box('Super 35 sensor',(0,0,sensor_z),(26.4/55,13.8/55,.004),'Sensor coating',.002)
        outline=[(-.32,-.16),(-.24,-.27),(.24,-.27),(.32,-.16),(.32,.16),(.24,.27),(-.24,.27),(-.32,.16)]
        cassette=profile('Cinema filter cassette',outline,z-.28,z-.21,'Anodized black',.012)
        bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,z-.245));opening=bpy.context.object;opening.scale=(.545,.395,.20)
        active(opening);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        cut=cassette.modifiers.new('Filter aperture','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=opening;apply(cassette,cut);bpy.data.objects.remove(opening,do_unlink=True)
        box('Cinema filter coating surround',(0,0,z-.255),(.541,.391,.008),'Sensor filter edge',.009)
        box('Cinema filter retaining border',(0,0,z-.249),(.485,.268,.004),'Gold engraving',.002)
        box('Cinema filter optical window',(0,0,z-.245),(.475,.258,.004),'Sensor coating',.002)
        for x in [-.23,.23]:
            for y in [-.315,.315]:screw((x,y,z-.16),r=.021)
    else:
        box('Sensor frame',(0,0,sensor_z-.015),(.48,.33,.025) if rf else (.53,.36,.025),'Anodized black',.018)
        if rf:box('Sensor filter surround',(0,0,sensor_z-.003),(.421,.285,.006),'Sensor filter edge',.003)
        box('APS-C sensor',(0,0,sensor_z),(22.3/55,14.8/55,.004) if rf else (.46,.30,.004),'Sensor coating' if rf else 'LCD glass',.002)
    if mirror:
        frame=box('Reflex mirror frame',(0,0,.17),(.56,.50,.018),'Anodized black',.008);frame.rotation_euler.x=-pi/4
        glass=box('Reflex mirror surface',(0,.009,.179),(.52,.46,.003),'Reflex mirror',.002);glass.rotation_euler.x=-pi/4
    for i in range(12 if rf else 10):
        a=pi*(1.18 if rf else 1.20)+i*(.18 if rf else .059);cyl('Gold electrical contact',(cos(a)*.455,sin(a)*.455,z+(.070 if rf else .032)),.012,.006,'Gold engraving',vertices=16)

def body(which):
    global current;current=which;start=len(OBJECTS);dslr=which=='40d'
    outline=[(-1.43,-.83),(-1.48,-.68),(-1.48,.38),(-1.41,.60),(-1.2,.69),(-.84,.66),(-.64,.64),(-.44,.78),(-.30,1.03 if dslr else .91),(.27,1.03 if dslr else .91),(.42,.77),(.65,.61),(.94,.53),(1.05,.38),(1.07,-.65),(.98,-.83)]
    if not dslr:
        outline=[(-1.43,-.83),(-1.48,-.65),(-1.48,.40),(-1.39,.65),(-1.19,.73),(-.83,.77),(-.48,.78),(-.34,.94),(.28,.94),(.43,.73),(.65,.64),(.92,.59),(1.05,.40),(1.07,-.65),(.98,-.83)]
    back=-.58 if dslr else -.39;front=.28 if dslr else .25
    shell=profile('Continuous cast housing',outline,back,front,'Crinkle painted metal',bevel=.055 if dslr else .085)
    if dslr:
        bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.445,depth=.88,location=(0,0,.05));bore=bpy.context.object
        cut=shell.modifiers.new('Open reflex mirror chamber','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=bore;apply(shell,cut);bpy.data.objects.remove(bore,do_unlink=True)
    if not dslr:
        for v in shell.data.vertices:
            x,y,z=v.co
            # The upper viewfinder housing reaches behind the shoulder plane.
            crest=max(0,min(1,(y-.34)/.4))*math.exp(-((x-.04)/.40)**4)
            rear_weight=max(0,min(1,(front-z)/(front-back)))
            v.co.z-=.115*crest*rear_weight
    # Full-depth ergonomic grip and a separate pebbled overmold follow the same contour.
    rows=[(-.85,-1.09,.11,.25,.32),(-.80,-1.12,.11,.33,.43),(-.65,-1.14,.12,.35,.46),(-.25,-1.15,.15,.355,.47),(.12,-1.14,.16,.345,.49),(.4,-1.16,.12,.33,.46),(.57,-1.19,.04,.29,.36),(.64,-1.21,-.02,.20,.24)]
    if not dslr:
        rows=[(-.85,-1.09,.30,.25,.37),(-.80,-1.12,.32,.32,.48),(-.65,-1.14,.32,.34,.53),(-.25,-1.15,.33,.355,.55),(.12,-1.14,.33,.345,.56),(.40,-1.16,.34,.32,.54),(.59,-1.19,.46,.28,.39),(.69,-1.20,.59,.20,.23),(.73,-1.20,.63,.12,.11)]
    # Keep the outside silhouette while narrowing the front grip into the
    # finger channel beside the mount, as seen in the R7 front reference.
    grip_rows=[(y,cx-rx*.20,cz,rx*.80,rz) for y,cx,cz,rx,rz in rows] if not dslr else rows
    grip_core=loft_grip('Sculpted grip core',grip_rows,'Crinkle painted metal')
    # Fuse both bodies' casting and grip; intersecting shells produce a hard
    # seam and unstable highlights across the 40D shutter shoulder.
    deck=box('Integrated LCD shoulder',(-.89,.615,-.18),(.93,.11,.63),'Crinkle painted metal',.045) if dslr else None
    active(shell);grip_core.select_set(True)
    if deck:deck.select_set(True)
    bpy.ops.object.join();OBJECTS.remove(grip_core)
    if deck:OBJECTS.remove(deck)
    remesh=shell.modifiers.new('Continuous grip and shoulder','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.012;remesh.use_smooth_shade=True;apply(shell,remesh)
    soften=shell.modifiers.new('Grip transition smoothing','SMOOTH');soften.factor=.65;soften.iterations=4;apply(shell,soften)
    reduce=shell.modifiers.new('Web mesh reduction','DECIMATE');reduce.ratio=.22;apply(shell,reduce)
    sleeve=[(y,cx,cz,rx+.004,rz+.004) for y,cx,cz,rx,rz in rows[1:5]]+[(.34,-1.15,.14,.34,.47),(.37,-1.16,.13,.331,.457)]
    if not dslr:
        sleeve=[(y,cx,cz,rx+.004,rz+.004) for y,cx,cz,rx,rz in rows[1:5]]+[(.34,-1.15,.34,.333,.551),(.39,-1.16,.34,.323,.545)]
    if not dslr:sleeve=[(y,cx-rx*.20,cz,rx*.80,rz) for y,cx,cz,rx,rz in sleeve]
    loft_grip('Textured grip overmold',sleeve,'Pebbled rubber')
    profile('Front leatherette panel',[(-.77,-.79),(-.75,.25),(-.58,.38),(-.52,.13),(-.5,-.4),(-.28,-.67),(.28,-.68),(.64,-.38),(.66,.35),(.96,.32),(.98,-.75)],front+.002,front+.016,'Pebbled rubber',.012)
    # Main body seam, shutter bezel, front lamp and release controls.
    if dslr:
        line('Grip molding seam',[(-1.45,.36,.26),(-1.32,.37,.52),(-1.12,.37,.615),(-.89,.35,.53),(-.83,.30,.40)],.004)
        sh=sphere('Shutter recess',(-1.2,.57,.37),(.145,.045,.16),'Deep black');sh.rotation_euler.x=.35
        sh=sphere('Shutter button',(-1.2,.60,.389),(.111,.037,.123),'Anodized black');sh.rotation_euler.x=.35
    else:
        sh=sphere('Shutter recess',(-1.25,.690,.748),(.142,.025,.109),'Deep black');sh.rotation_euler.x=.32
        sh=sphere('Shutter button',(-1.25,.708,.754),(.111,.018,.079),'Anodized black');sh.rotation_euler.x=.32
    sphere('AF assist lamp',(-.69,.49,front+.053),(.046,.046,.02),'LCD glass')
    if dslr:
        # Loft regular longitudinal quads instead of deforming a bevelled
        # extrusion. End support rings round the lip without shading strips.
        outline_flash=[(-.49,.80),(-.42,.94),(-.29,1.075),(.29,1.075),(.42,.94),(.49,.80)]
        outline_flash.reverse()
        corners=smooth_outline(outline_flash,8);section=[]
        for a,b in zip(corners,corners[1:]+corners[:1]):
            steps=max(1,int(np.ceil(np.linalg.norm(b-a)/.025)))
            section.extend(a+(b-a)*i/steps for i in range(steps))
        n=len(section)
        stations=[0,.012,.035]+[i/24 for i in range(1,24)]+[.965,.988,1]
        stations=sorted(set(stations));verts=[];faces=[]
        for t in stations:
            end_round=.016*(1-sin(pi*min(1,t/.035,(1-t)/.035)/2))
            for x,y in section:
                upper=max(0,min(1,(y-.80)/.275))
                crown=-.03*(1-t)-.09*t+.035*sin(pi*t)
                # Reference underside rises slightly toward the front lip.
                yy=y+crown*upper-.025*(1-t)*(1-upper)
                verts.append((x*(1-.20*t)*(1-end_round/.49),yy+( .925-yy)*end_round/.125,-.36+.915*t))
        for row in range(len(stations)-1):
            for i in range(n):
                j=(i+1)%n;faces.append((row*n+i,row*n+j,(row+1)*n+j,(row+1)*n+i))
        faces.extend([tuple(reversed(range(n))),tuple(range((len(stations)-1)*n,len(stations)*n))])
        mesh=bpy.data.meshes.new('Flash hood loft');mesh.from_pydata(verts,[],faces);mesh.update()
        flash=bpy.data.objects.new('Pop-up flash cover',mesh);scene.collection.objects.link(flash);register(flash,'Pop-up flash cover','Graphite polymer')
        for face in mesh.polygons:face.use_smooth=len(face.vertices)==4
        # A narrow pocket keeps the two moulded parts from intersecting.
        cavity=flash.copy();cavity.data=flash.data.copy();scene.collection.objects.link(cavity)
        # Remove the original crown outside the new cover as well as inside it.
        # A normal-offset copy left small exterior shell islands visible through
        # the tapered hood near y=.96, z=.24.
        for v in cavity.data.vertices:
            v.co.x*=1.25
            v.co.y+=.14*max(0,min(1,(v.co.y-.80)/.20))
        cavity.data.update()
        cut=shell.modifiers.new('Flash cover seating pocket','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=cavity;apply(shell,cut)
        bpy.data.objects.remove(cavity,do_unlink=True)
        line('Flash cover front seam',[(x*.8,y-.09*max(0,min(1,(y-.8)/.275)),.559) for x,y in [(-.46,.82),(-.37,.95),(-.27,1.035),(.27,1.035),(.37,.95),(.46,.82)]],.003)
        cyl('Flash release',(1.073,.37,.12),.05,.027,'Graphite polymer','x',48)
    text('Canon wordmark','Canon',(0,.896 if dslr else .840,.561 if dslr else front+.006),.12,font='Canon')
    text('EOS badge','EOS',(.84,.35 if dslr else .36,front+(.043 if dslr else .040)),.075)
    text('Model badge','40D' if dslr else 'R7',(.84,.245 if dslr else .205,front+(.044 if dslr else .041)),.084 if dslr else .090)
    if not dslr:box('Raised R7 badge',(.84,.285,front+.026),(.245,.30,.015),'Graphite polymer',.036)
    if dslr:box('Raised model badge',(.84,.295,front+.027),(.245,.26,.027),'Anodized black',.038)
    cyl('Lens release bezel',(.69,-.06,.35),.099,.1,'Deep black')
    cyl('Lens release button',(.70,-.05,.412),.069,.025,'Graphite polymer')
    if dslr:cyl('Depth preview',(-1.1,-.37,.61),.061,.025,'Graphite polymer')
    if not dslr:
        cyl('AF MF selector',(-.71,-.59,.338),.10,.04,'Anodized black');cyl('AF MF selector center',(-.71,-.59,.365),.058,.015,'Graphite polymer');text('Focus mode legend','MF\nAF',(-.91,-.59,.335),.039)
    mountStart=len(OBJECTS)
    mount(.48,mirror=dslr,rf=not dslr)
    mount_objects=set(OBJECTS[mountStart:])
    # Top: shoe channels, contact pins, textured command dial and mode wheel.
    shoeY=1.072 if dslr else .974
    box('Hot shoe base',(0,shoeY,-.10),(.48,.045,.43),'Anodized black',.017)
    for x in [-.205,.205]:
        box('Hot shoe rail',(x,shoeY+.032,-.1),(.06,.033,.4),'Machined metal',.008)
        box('Hot shoe return',(x+(.018 if x<0 else -.018),shoeY+.056,-.1),(.04,.017,.39),'Machined metal',.005)
    for x,z in [(0,-.1),(-.09,-.20),(.09,-.20),(-.05,.0),(.05,.0)]:cyl('Flash contact',(x,shoeY+.03,z),.015,.008,'Gold engraving','y',24,.001)
    if dslr:
        dial((.76,.615,-.10),.23,'y','40d')
        dial((-1.20,.53,.16),.12,'x',width=.23)
    else:
        # R7's mode dial is beside the hot shoe, on the grip shoulder.
        dial((-.63,.782,-.035),.185,'y','r7')
        dial((-1.20,.608,.448),.114,'x',width=.265)
    if dslr:
        # The status window is recessed into the continuous shoulder casting.
        opening=box('Top LCD cutter',(-.87,.685,-.27),(.744,.22,.394),None,.028)
        cut=shell.modifiers.new('Recessed top status display','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=opening;apply(shell,cut)
        OBJECTS.remove(opening);bpy.data.objects.remove(opening,do_unlink=True)
        bezel=box('Top LCD surround',(-.87,.659,-.27),(.736,.028,.386),'Deep black',.028)
        window=box('Top LCD bezel opening',(-.87,.659,-.27),(.68,.08,.33),None,.019)
        cut=bezel.modifiers.new('Open status display bezel','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=window;apply(bezel,cut)
        OBJECTS.remove(window);bpy.data.objects.remove(window,do_unlink=True)
        box('Top LCD',(-.87,.665,-.27),(.67,.008,.32),'LCD display',.019)
        # Faint inactive segment outlines, as in the powered-off reference.
        for name,points in [
            ('Left status field',[(-.58,-.13),(-.73,-.13),(-.73,-.25),(-.80,-.25),(-.80,-.36),(-.58,-.36),(-.58,-.13)]),
            ('AF status field',[(-.83,-.15),(-.99,-.15),(-.99,-.23),(-.83,-.23),(-.83,-.15)]),
            ('Right status field',[(-1.04,-.13),(-1.16,-.13),(-1.16,-.40),(-1.04,-.40),(-1.04,-.13)]),
        ]:line(name,[(x,.670,z) for x,z in points],.0012,'Inactive LCD segments')
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        top_surface=BVHTree.FromObject(shell,bpy.context.evaluated_depsgraph_get())
        for i,t in enumerate(['LIGHT','WB','AF-DRIVE','ISO']):
            x=-.56-i*.205
            hit,_,_,_=top_surface.ray_cast(Vector((x,2,.055)),Vector((0,-1,0)),4)
            if hit is None:raise RuntimeError('Top function button missed shoulder')
            sphere('Top function button '+t,(x,hit.y+.012,.055),(.037,.020,.035),'Graphite polymer')
            label=text('Top legend '+t,t,(x,.677,-.016),.025)
            label.matrix_world=Matrix.Translation(label.location)@Matrix.Rotation(-pi/2,4,'X')@Matrix.Rotation(pi,4,'Z')
            active(label);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
            for v in label.data.vertices:
                hit,_,_,_=top_surface.ray_cast(Vector((v.co.x,2,v.co.z)),Vector((0,-1,0)),4)
                if hit is None:raise RuntimeError('Top function label missed shoulder')
                v.co.y=hit.y+.003
    else:
        for name,x,y,z in [('M-Fn',-1.015,.677,.575),('ISO',-1.25,.735,.185),('LOCK',-.97,.751,-.095),('Record',-1.015,.745,.200)]:
            cyl('Top '+name+' bezel',(x,y-.006,z),.060,.016,'Deep black','y',48)
            sphere('Top '+name+' button',(x,y+.008,z),(.043,.015,.043),'Graphite polymer')
            if name=='Record':cyl('Record button red dot',(x,y+.024,z),.019,.002,'Red lacquer','y',32,.001)
            else:
                label=text('Top '+name+' marking',name,(x,y+.01,z-.095) if name=='LOCK' else (x-.105,y+.01,z) if name=='M-Fn' else (x+.105,y+.01,z),.033)
                label.matrix_world=Matrix.Translation(label.location)@Matrix.Rotation(-pi/2,4,'X')@Matrix.Rotation(pi,4,'Z')
        cyl('Power selector bezel',(-1.225,.718,-.242),.123,.022,'Deep black','y',64)
        cyl('Power selector',(-1.225,.734,-.242),.106,.021,'Graphite polymer','y',64)
        box('Power lever',(-1.225,.754,-.305),(.026,.021,.125),'Focus rubber',.010)
        label=text('Power legend','ON OFF',(-1.225,.759,-.08),.032)
        label.matrix_world=Matrix.Translation(label.location)@Matrix.Rotation(-pi/2,4,'X')@Matrix.Rotation(pi,4,'Z')
        # Printed legends follow the curved casting, including the sloped grip.
        from mathutils.bvhtree import BVHTree
        surface=BVHTree.FromObject(shell,bpy.context.evaluated_depsgraph_get())
        for o in OBJECTS[start:]:
            if ('Top ' in o.name and ' marking' in o.name) or 'Power legend' in o.name:
                active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
                for v in o.data.vertices:
                    hit,normal,_,_=surface.ray_cast(Vector((v.co.x,2,v.co.z)),Vector((0,-1,0)),4)
                    if hit is not None:v.co.y=hit.y+.003
    # Back screen and control layout differ between the two cameras.
    rz=back-.042;screenX=.30 if dslr else .18;screenW=1.30 if dslr else 1.73;screenH=1.02 if dslr else 1.12;screenY=-.12 if dslr else -.24
    # Rear controls are seated in a separate rear cover. Their bezels were
    # previously suspended in front of the main casting's flat back plane.
    rear_cover=profile('Rear control cover',outline,back-.083,back+.012,'Crinkle painted metal',.030)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(screenX,screenY,back-.06))
    opening=bpy.context.object;opening.scale=(screenW-.06,screenH-.08,.30)
    active(opening);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    cut=rear_cover.modifiers.new('LCD opening in rear cover','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=opening;apply(rear_cover,cut);bpy.data.objects.remove(opening,do_unlink=True)
    if not dslr:
        # Two barrel sections and the central joint visible in the rear reference.
        for offset in [-.28,.28]:
            box('LCD hinge barrel',(.99,screenY+offset,rz-.012),(.15,.53,.15),'Graphite polymer',.030)
        box('LCD hinge center joint',(.99,screenY,rz-.016),(.145,.016,.142),'Deep black',.006)
    # The 40D's old bezel rear face lay inside the cover, leaving a razor-thin
    # edge. Seat the frame outside the cover and the glass just in front of it.
    bezel_z=rz-.057 if dslr else rz
    box('LCD bezel',(screenX,screenY,bezel_z),(screenW,screenH,.055 if dslr else .115),'Deep black',.045)
    glass_z=rz-.088 if dslr else rz-.066
    glass_w=screenW-.12;glass_h=screenH-.15
    box('LCD perimeter gasket',(screenX,screenY+.015,glass_z+.003),(glass_w+.024,glass_h+.024,.010),'Graphite polymer',.032)
    box('LCD cover glass',(screenX,screenY+.015,glass_z-.003),(glass_w,glass_h,.010),'Inactive display glass',.026)
    if dslr:text('Rear Canon logo','Canon',(screenX,screenY-screenH/2+.047,rz-.087),.058,rotation=(0,pi,0),font='Canon')
    eyecup(.04,.69,rz,which)
    if dslr:
        rear_thumb=profile('40D rear thumb overmold',[(-.54,.61),(-1.28,.58),(-1.40,.32),(-1.38,-.74),(-.97,-.74),(-.91,-.60),(-1.06,-.39),(-1.09,-.17),(-.96,.02),(-.56,.08)],rz-.069,rz-.037,'Pebbled rubber',.012)
        cyl('Quick control recess',(-.73,-.32,rz-.031),.355,.035,'Deep black')
        ring('Quick wheel rim',rz-.063,.315,.292,.037,'Graphite polymer',center=(-.73,-.32))
        ring('Quick wheel rubber face',rz-.079,.301,.244,.029,'Focus rubber',center=(-.73,-.32))
        for i in range(88):
            a=i*2*pi/88
            tooth=box('Rear wheel radial grip',(-.73+cos(a)*.273,-.32+sin(a)*.273,rz-.101),(.047,.011,.013),'Focus rubber',.004);tooth.rotation_euler.z=a
        ring('Quick wheel bowl outer',rz-.073,.246,.182,.022,'Graphite polymer',center=(-.73,-.32))
        ring('Quick wheel bowl inner',rz-.061,.186,.085,.022,'Graphite polymer',center=(-.73,-.32))
        cyl('SET button socket',(-.73,-.32,rz-.068),.095,.017,'Deep black')
        sphere('SET button',(-.73,-.32,rz-.084),(.080,.080,.016),'Graphite polymer')
        text('SET legend','SET',(-.73,-.32,rz-.102),.037,rotation=(0,pi,0))
        cyl('Multi controller socket',(-.52,.24,rz-.038),.119,.035,'Deep black')
        sphere('Multi controller',(-.52,.24,rz-.072),(.080,.080,.039),'Graphite polymer')
        sphere('Multi controller tip',(-.52,.24,rz-.106),(.048,.048,.013),'Focus rubber')
        sphere('Rear power recess',(-.34,-.74,rz-.032),(.145,.09,.027),'Deep black')
        lever=box('Rear power lever',(-.35,-.74,rz-.066),(.23,.045,.029),'Graphite polymer',.015);lever.rotation_euler.z=.06
        text('Rear power markings','ON\nOFF',(-.53,-.75,rz-.045),.032,rotation=(0,pi,0))
    else:
        # Rear R7 reference: a deeply recessed joystick inside a knurled wheel,
        # plus a separate four-way rocker below the sculpted thumb overmold.
        x,y=-.62,.62
        cyl('Rear wheel recess',(x,y,rz-.047),.232,.024,'Deep black')
        ring('Rear wheel outer lip',rz-.074,.218,.202,.032,'Graphite polymer',center=(x,y))
        ring('Rear quick control ring',rz-.092,.202,.147,.050,'Focus rubber',center=(x,y))
        rib=radial_ribs('Rear wheel edge knurl',rz-.096,.202,.037,96);rib.location.x=x;rib.location.y=y
        cyl('Joystick socket',(x,y,rz-.070),.141,.021,'Deep black')
        sphere('Joystick rubber cup',(x,y,rz-.094),(.100,.100,.021),'Focus rubber')
        sphere('Joystick thumb tip',(x,y,rz-.118),(.064,.064,.015),'Pebbled rubber')
        for ix in range(-3,4):
            for iy in range(-3,4):
                if ix*ix+iy*iy<12:sphere('Joystick molded dots',(x+ix*.014,y+iy*.014,rz-.134),(.003,.003,.002),'Graphite polymer')
        profile('Rear thumb rubber',[(-1.40,-.66),(-1.41,.27),(-1.31,.53),(-1.23,.54),(-1.16,.38),(-.89,.32),(-.86,.17),(-1.02,.03),(-1.08,-.17),(-1.12,-.42),(-1.17,-.66)],rz-.068,rz-.037,'Pebbled rubber',.012)
        x,y=-.90,-.35
        cyl('Four way pad recessed bezel',(x,y,rz-.047),.211,.025,'Deep black')
        ring('Four way pad rim',rz-.069,.201,.181,.021,'Graphite polymer',center=(x,y))
        sphere('Four way rocker',(x,y,rz-.073),(.178,.178,.025),'Graphite polymer')
        cyl('SET button recess',(x,y,rz-.095),.079,.012,'Deep black')
        sphere('SET button',(x,y,rz-.108),(.064,.064,.013),'Anodized black')
        text('Q SET','Q\nSET',(x,y,rz-.124),.043,rotation=(0,pi,0))
        for a in [0,pi/2,pi,3*pi/2]:
            notch=box('Rocker direction notch',(x+cos(a)*.150,y+sin(a)*.150,rz-.096),(.042,.008,.005),'Deep black',.002);notch.rotation_euler.z=a
    rear_buttons=[(-1.36,.51,'*'),(-1.36,.35,'▣'),(-1.0,.52,'AF-ON'),(-.78,.08,'INFO'),(-.87,-.66,'▶'),(-1.07,-.66,'▥'),(.83,.52,'MENU')]
    if dslr:rear_buttons=[(-.89,.55,'AF-ON'),(-1.08,.53,'*'),(-1.27,.48,'▣'),(.85,.42,'MENU'),(.65,.45,'LV'),(.84,-.76,'▶'),(.62,-.76,'▥'),(.40,-.76,'JUMP'),(.18,-.76,'INFO'),(-.05,-.76,'STYLE')]
    for x,y,t in rear_buttons:
        cyl('Rear button bezel '+t,(x,y,rz-.047),.071,.018,'Deep black')
        sphere('Rear button '+t,(x,y,rz-.063),(.055,.055,.020),'Graphite polymer')
        on_button=t!='AF-ON'
        if t=='▶':
            line('Playback icon',[(x+.018,y+.02,rz-.086),(x-.021,y,rz-.086),(x+.018,y-.02,rz-.086),(x+.018,y+.02,rz-.086)],.003,'Blue ink')
        elif t=='▣':
            # AF-point selection is a framed point array, not the erase symbol.
            iy=y+.086 if dslr else y
            iz=rz-.045 if dslr else rz-.086
            line('AF point frame',[(x-.024,iy-.018,iz),(x+.024,iy-.018,iz),(x+.024,iy+.018,iz),(x-.024,iy+.018,iz),(x-.024,iy-.018,iz)],.002,'White ink')
            for dx,dy in [(0,0),(-.014,0),(.014,0),(0,-.01),(0,.01)]:
                box('AF point',(x+dx,iy+dy,iz),(.005,.005,.001),'White ink',0)
        elif t=='▥':
            line('Erase icon',[(x-.018,y+.014,rz-.086),(x-.014,y-.021,rz-.086),(x+.014,y-.021,rz-.086),(x+.018,y+.014,rz-.086)],.0025,'Blue ink')
            line('Erase lid',[(x-.023,y+.023,rz-.086),(x+.023,y+.023,rz-.086)],.003,'Blue ink')
        else:text('Rear label '+t,t,(x,y+.086 if dslr else y if on_button else y-.09,rz-.045 if dslr else rz-.085),.045 if dslr else .040,rotation=(0,pi,0))
    if dslr:
        # Legends printed beside the buttons belong on the outer cover or
        # rubber overmold. A shared Z plane buried the AE/AF markings in rubber.
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        rear_surfaces=[BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get()) for o in [rear_cover,rear_thumb]]
        for o in OBJECTS[start:]:
            if not any(part in o.name for part in ['Rear label','Rear power markings','AF point frame','AF point.',' / AF point']):continue
            active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
            backmost=max(v.co.z for v in o.data.vertices)
            for v in o.data.vertices:
                hits=[bvh.ray_cast(Vector((v.co.x,v.co.y,-3)),Vector((0,0,1)),4)[0] for bvh in rear_surfaces]
                hits=[hit for hit in hits if hit is not None]
                if not hits:raise RuntimeError('Rear legend missed the cover: '+o.name)
                v.co.z=min(hit.z for hit in hits)-.003+(v.co.z-backmost)
    # Both sides carry door seams, strap eyelets and tiny fasteners.
    for x in [-1.42,1.04]:
        box('Strap lug seat',(x,.38,-.09),(.07,.18,.21),'Graphite polymer',.022)
        eye=ring('Strap eye',0,.051,.027,.026,'Machined metal');eye.rotation_euler.y=pi/2;eye.location=(x,.39,-.1)
    if dslr:
        # The 40D has two tall adjacent rubber terminal flaps, not horizontal
        # subdivisions. Their seam and molded legends are visible from the side.
        terminal_start=len(OBJECTS)
        box('Terminal cover recessed surround',(1.080,-.17,-.10),(.032,.91,.55),'Deep black',.027)
        for zz in [-.235,.035]:
            box('40D terminal flap',(1.099,-.17,zz),(.025,.858,.249),'Focus rubber',.025)
            box('Terminal flap top finger lip',(1.114,.174,zz),(.015,.035,.207),'Graphite polymer',.009)
        text('Video out molded legend','VIDEO\nOUT',(1.114,.072,-.235),.043,'Deep black',rotation=(0,pi/2,0))
        # Flash sync and remote-control symbols are molded into the other flap.
        line('Sync flash symbol',[(1.114,.12,.055),(1.114,.015,.075),(1.114,.035,.030),(1.114,-.055,.048)],.006,'Deep black')
        line('Remote socket symbol',[(1.114,-.30,.075),(1.114,-.26,.075),(1.114,-.24,.035),(1.114,-.26,-.005),(1.114,-.30,-.005)],.004,'Deep black')
        line('USB stem',[(1.114,-.42,-.235),(1.114,-.29,-.235)],.004,'Deep black')
        line('USB left branch',[(1.114,-.37,-.235),(1.114,-.34,-.20),(1.114,-.30,-.20)],.004,'Deep black')
        line('USB right branch',[(1.114,-.39,-.235),(1.114,-.35,-.27),(1.114,-.32,-.27)],.004,'Deep black')
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        terminal_surface=BVHTree.FromObject(shell,bpy.context.evaluated_depsgraph_get())
        for o in OBJECTS[terminal_start:]:
            active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
            if any(part in o.name for part in ['surround','flap']):
                import bmesh
                bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=8,use_grid_fill=True);bm.to_mesh(o.data);bm.free()
            for v in o.data.vertices:
                hit,_,_,_=terminal_surface.ray_cast(Vector((3,v.co.y,v.co.z)),Vector((-1,0,0)),4)
                if hit is None:raise RuntimeError('Terminal cover missed casting: '+o.name)
                v.co.x=hit.x+(v.co.x-1.080)*.45
            o.data.update()
        # Project the CF-card door perimeter onto the actual outer casting and
        # grip, keeping the seam attached as the side transitions into the grip.
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        side_surfaces=[(shell,BVHTree.FromObject(shell,bpy.context.evaluated_depsgraph_get()))]
        border=[(.23,-.51),(.23,-.12),(.16,-.075),(-.66,-.075),(-.71,-.13),(-.71,-.49),(-.66,-.54),(.16,-.54),(.23,-.51)]
        points=[]
        for a,b in zip(border,border[1:]):
            for j in range(12):
                t=j/12;yy=a[0]*(1-t)+b[0]*t;zz=a[1]*(1-t)+b[1]*t;hits=[]
                for obj,bvh in side_surfaces:
                    hit,_,_,_=bvh.ray_cast(Vector((-3,yy,zz)),Vector((1,0,0)),4)
                    if hit is not None:hits.append(hit.x)
                if not hits:raise RuntimeError('CF door seam missed the body surface')
                points.append((min(hits)-.002,yy,zz))
        points.append(points[0]);line('CF card door perimeter',points,.0035,'Deep black')
    else:
        box('Connector door',(1.08,-.22,-.1),(.04,.8,.43),'Pebbled rubber',.023)
        for y in [-.06,-.29]:line('Port flap seam',[(1.105,y,-.28),(1.105,y,.06)],.003)
    for z in [-.20,.07]:
        x=1.108
        if dslr:
            hit,_,_,_=terminal_surface.ray_cast(Vector((3,-.68,z)),Vector((-1,0,0)),4)
            if hit is None:raise RuntimeError('Side fastener missed casting')
            x=hit.x+.002
        screw((x,-.68,z),'x',.017)
    box('Battery plate',(-.70,-.821,-.08),(.82,.020,.57),'Graphite polymer',.016)
    # The tripod thread is recessed into the base, not a protruding silver peg.
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.063,depth=.09,location=(0,-.814,-.07),rotation=(pi/2,0,0))
    bore=bpy.context.object;cut=shell.modifiers.new('Recessed tripod thread','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=bore;apply(shell,cut);bpy.data.objects.remove(bore,do_unlink=True)
    for y,outer,inner in [(-.828,.076,.062),(-.817,.064,.056),(-.805,.064,.056)]:
        lip=ring('Tripod socket thread',0,outer,inner,.006,'Machined metal');lip.rotation_euler.x=pi/2;lip.location=(0,y,-.07)
    cyl('Tripod socket dark interior',(0,-.781,-.07),.060,.006,'Deep black','y',48)
    # Keep side controls on the casting. Moving only object origins outward does
    # not widen the shell mesh, and had left the 40D doors and strap mounts floating.
    if not dslr:
        # Reference front view: the right shoulder is narrow and the body is
        # shorter than the earlier generic DSLR-like housing. Apply the same
        # deformation to attached controls so none float beyond the new shell.
        for o in OBJECTS[start:]:
            if o in mount_objects:continue
            active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
            rigid_shoe=any(part in o.name for part in ['Hot shoe','Flash contact'])
            for v in o.data.vertices:
                # The R7 top is a sculpted crown rather than a straight extrusion.
                # Carry its badges and controls through the same deformation so
                # the projecting finder brow and rounded deck remain continuous.
                x,y,z=v.co
                upper=max(0,min(1,(y-.40)/.35));upper=upper*upper*(3-2*upper)
                front_weight=max(0,min(1,(z-back)/(front-back)))
                finder=math.exp(-(x/.48)**4)
                if not rigid_shoe:v.co.z+=.17*finder*upper*front_weight
                crown=max(0,min(1,(y-.35)/.35));crown=crown*crown*(3-2*crown)
                v.co.y+=.045 if rigid_shoe else .045*crown*math.exp(-((z+.06)/.26)**4)
                v.co.y*=.87
                if v.co.x>.45 and 'Lens release' not in o.name:
                    v.co.x=.45+(v.co.x-.45)*.65
            o.data.update()
        # Keep the RF opening circular after the housing proportions change.
        bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=.436,depth=.80,location=(0,0,.15));bore=bpy.context.object
        cut=shell.modifiers.new('Open RF sensor chamber','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=bore;apply(shell,cut);bpy.data.objects.remove(bore,do_unlink=True)
    return OBJECTS[start:]

def fifty_prime():
    # EF 50mm f/1.8 II: smooth plastic barrel, narrow front focusing rim,
    # no distance window, and a small optical group recessed inside a wide cone.
    global current;current='50';start=len(OBJECTS)
    ring('Plastic EF bayonet',.044,.535,.36,.088,'Graphite polymer')
    ring('Mount shoulder',.14,.59,.36,.16,'Graphite polymer')
    ring('Smooth fixed barrel',.405,.62,.48,.43,'Graphite polymer')
    ring('Rear barrel joint',.205,.622,.605,.009,'Deep black')
    ring('Focus ring separation',.635,.622,.60,.014,'Deep black')
    ring('Narrow manual focus rim',.684,.62,.563,.083,'Graphite polymer')
    radial_ribs('Front focus serrations',.684,.62,.073,160)
    ring('Front inscription rim',.735,.617,.544,.028,'Graphite polymer')
    ring('Filter socket',.690,.547,.473,.063,'Anodized black')
    for j in range(6):ring('52mm filter thread',.713-j*.009,.481,.469,.004,'Graphite polymer')
    # Continuous conical surface avoids overlapping beveled annuli and their
    # moire at browser resolution; the real recess has a fine matte finish.
    vertices=[];faces=[];segments=192
    for radius,z in [(.470,.674),(.300,.548)]:
        vertices.extend((radius*cos(i*2*pi/segments),radius*sin(i*2*pi/segments),z) for i in range(segments))
    for i in range(segments):
        j=(i+1)%segments;faces.append((i,j,segments+j,segments+i))
    mesh=bpy.data.meshes.new('Continuous front recess');mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new('Continuous front recess',mesh);scene.collection.objects.link(o);register(o,'Continuous front recess','Deep black')
    for face in mesh.polygons:face.use_smooth=True
    ring('Front element retaining lip',.542,.302,.278,.025,'Anodized black')
    optical_element('Optical front element',.530,.278,.022,.025)
    optical_element('Optical inner element',.375,.257,.017,.022,'Inner optical glass')
    ring('Iris seat',.265,.275,.185,.012,'Anodized black')
    for i in range(5):
        a=i*2*pi/5;b=a+2*pi/5
        pts=[(.185*cos(a),.185*sin(a),.275),(.185*cos(b),.185*sin(b),.275),(.273*cos(b),.273*sin(b),.274),(.273*cos(a-.1),.273*sin(a-.1),.274)]
        mesh=bpy.data.meshes.new('Five blade iris');mesh.from_pydata(pts,[],[(0,1,2,3)])
        o=bpy.data.objects.new('Five blade iris',mesh);scene.collection.objects.link(o);register(o,'Iris blade','Anodized black')
    optical_element('Optical rear element',.16,.24,.017,.021)
    arc_text('CANON LENS EF 50mm 1:1.8 II',.751,.578,.047,start=2.0,span=2.9)
    arc_text('CANON INC.   Ø52mm',.751,.578,.034,start=-pi*.73,span=1.45)
    # Bend both printed legends and the compact AF/MF recess onto the shell.
    detail_start=len(OBJECTS)
    box('AF MF recess',(0,0,0),(.235,.23,.012),'Deep black',.018)
    text('AF MF legend','AF  MF',(0,.060,.012),.039)
    box('Focus mode track',(0,-.037,.013),(.145,.055,.011),'Deep black',.009)
    box('Focus mode slider',(-.033,-.037,.026),(.066,.053,.025),'Graphite polymer',.012)
    for o in OBJECTS[detail_start:]:
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        for v in o.data.vertices:
            u,vv,depth=v.co;angle=vv/.62;rad=.62+depth
            v.co=(-rad*cos(angle),rad*sin(angle),.39+u)
    text('Fixed focal length','50mm',(0,.624,.41),.078,rotation=(-pi/2,0,0))
    text('Minimum focusing distance','0.45m / 1.5ft',(0,.624,.30),.031,'Gold engraving',rotation=(-pi/2,0,0))
    sphere('Mount alignment pip',(-.622,-.16,.245),(.014,.018,.018),'Red lacquer')
    for i in range(8):
        a=pi*1.15+i*.075;cyl('Lens electrical contact',(cos(a)*.468,sin(a)*.468,.012),.013,.012,'Gold engraving',vertices=16)
    return OBJECTS[start:]

def tamron_prime():
    global current;current='35';start=len(OBJECTS)
    # Canon F045 dimensions: 104.8mm mount-to-tip, 80.9mm maximum diameter.
    length=104.8/55;radius=80.9/110
    ring('EF bayonet',.044,.535,.40,.088,'Machined metal')
    ring('Rear weather seal',.10,.56,.40,.026,'Deep black')
    # Revolve the tapered rear neck and broad pale accent as one smooth contour.
    for name,rows,mat in [
        ('Pale mount accent',[(.565,.12),(.59,.145),(.597,.21),(.616,.27),(.637,.30)],'Machined metal'),
        ('Tapered rear shoulder',[(.637,.30),(.651,.32),(.719,.43),(.722,.47)],'Graphite polymer')]:
        verts=[];faces=[];n=192
        for rr,z in rows:verts.extend((rr*cos(i*2*pi/n),rr*sin(i*2*pi/n),z) for i in range(n))
        for j in range(len(rows)-1):
            for i in range(n):k=(i+1)%n;faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
        o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);register(o,name,mat)
        for face in mesh.polygons:face.use_smooth=True
    ring('Smooth rear barrel',.81,.722,.59,.69,'Graphite polymer')
    ring('Focus ring rear seam',1.17,.723,.70,.015,'Deep black')
    ring('Manual focus grip',1.46,radius-.01,.68,.55,'Focus rubber')
    radial_ribs('Fine focus grip lands',1.46,radius-.008,.53,180)
    ring('Front focus seam',1.75,.724,.70,.011,'Deep black')
    ring('Hood bayonet base',1.805,.716,.651,.09,'Graphite polymer')
    ring('Front filter socket',length-.033,.697,.651,.066,'Anodized black')
    for j in range(7):ring('72mm filter thread',length-.012-j*.009,.656,.649,.004,'Deep black')
    ring('Front optical surround',length-.095,.650,.535,.034,'Deep black')
    ring('Front glass retaining lip',length-.120,.539,.513,.024,'Anodized black')
    optical_element('Optical front element',length-.153,.513,.047,.029)
    optical_element('Optical inner element',length-.45,.421,.024,.023,'Inner optical glass')
    optical_element('Optical rear element',.28,.33,.022,.024,'Inner optical glass')
    ring('Internal optical barrel',.89,.598,.48,1.07,'Deep black')
    ring('Iris housing',.72,.48,.225,.012,'Anodized black')
    # Distance window and all its legends are conformed onto the barrel.
    detail_start=len(OBJECTS)
    box('Distance window surround',(0,0,0),(.46,.20,.022),'Anodized black',.027)
    box('Distance window glass',(0,0,.015),(.423,.166,.013),'LCD glass',.023)
    text('Distance feet','3     ∞',(-.012,.025,.024),.044)
    text('Distance metres','1     ∞',(-.012,-.038,.024),.044)
    text('Distance units','ft',(.255,.033,.025),.034)
    text('Distance units','m',(.255,-.034,.025),.034)
    text('Tamron brand','TAMRON',(0,.160,.013),.065,font='Bold')
    text('Focus index','I',(0,-.156,.013),.054)
    text('Lens model','SP 35mm F/1.4',(.53,.053,.012),.037)
    text('Lens drive','Di USD',(.48,-.018,.012),.037)
    for o in OBJECTS[detail_start:]:
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if any(part in o.name for part in ['window','panel','inset']):
            import bmesh
            bm=bmesh.new();bm.from_mesh(o.data)
            bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=12,use_grid_fill=True)
            bm.to_mesh(o.data);bm.free()
        for v in o.data.vertices:
            u,vv,d=v.co;angle=u/.722;rr=.722+d
            v.co=(-rr*sin(angle),rr*cos(angle),.88+vv)
    detail_start=len(OBJECTS)
    box('AF MF panel',(0,0,0),(.30,.55,.017),'Graphite polymer',.05)
    box('AF MF inset',(0,0,.01),(.255,.505,.012),'Deep black',.043)
    box('Switch slot',(0,0,.026),(.10,.23,.011),'Deep black',.04)
    box('AF slider',(0,.047,.038),(.076,.105,.018),'Graphite polymer',.026)
    text('AF legend','AF',(0,.17,.025),.034)
    text('MF legend','MF',(0,-.17,.025),.034)
    for o in OBJECTS[detail_start:]:
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if any(part in o.name for part in ['window','panel','inset']):
            import bmesh
            bm=bmesh.new();bm.from_mesh(o.data)
            bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=12,use_grid_fill=True)
            bm.to_mesh(o.data);bm.free()
        for v in o.data.vertices:
            u,vv,d=v.co;angle=vv/.722;rr=.722+d
            v.co=(-rr*cos(angle),rr*sin(angle),.66+u)
    sphere('Mount alignment',(0,.641,.306),(.009,.007,.025),'White ink')
    sphere('Hood alignment',(0,.717,1.807),(.007,.006,.007),'White ink')
    for i in range(8):
        a=pi*1.15+i*.075;cyl('Lens electrical contact',(cos(a)*.468,sin(a)*.468,.012),.013,.012,'Gold engraving',vertices=16)
    return OBJECTS[start:]

def lens(which):
    if which=='50':return fifty_prime()
    if which=='35':return tamron_prime()
    global current;current=which;start=len(OBJECTS)
    specs={'28-135':(1.76,.713,'28-135mm','1:3.5-5.6',72), '70-200-f4':(3.12,.69,'70-200mm','1:4',67),'70-200-f28':(3.62,.805,'70-200mm','1:2.8',77),'35':(1.82,.735,'35mm','1:1.4',72),'50':(.75,.625,'50mm','1:1.8',52)}
    l,r,range_,aperture,thread=specs[which];white=which.startswith('70-200');paint='White enamel' if white else 'Graphite polymer'
    # Hollow, stepped barrel: no opaque disk in front of the optical assembly.
    ring('EF bayonet',.044,.535,.43,.088,'Machined metal');ring('Rear gasket',.09,.55,.425,.034,'Deep black')
    ring('Mount end',.19,r*.82,.41,.18,'Anodized black');ring('Taper shoulder',.32,r*.92,.43,.08,paint)
    barrel_start=.265;barrel_end=l-.045
    housing=ring('Main lens housing',(barrel_start+barrel_end)/2,r*.97,r*.79,barrel_end-barrel_start,paint)
    ring('Interior flocking',l*.5,r*.794,r*.78,l-.25,'Deep black')
    if white:
        for z,width in ([(l*.37,l*.26),(l*.76,l*.22)] if which=='70-200-f4' else [(l*.37,l*.16),(l*.76,l*.16)]):
            ring('Rubber ring',z,r*.997,r*.89,width,'Focus rubber');radial_ribs('Molded longitudinal grip ribs',z,r*.997,width*.92,144)
        ring('L-series red ring',l*.92,r*.992,r*.94,.034,'Red lacquer')
        collar_z=l*(.18 if which=='70-200-f4' else .22)
        ring('Tripod collar',collar_z,r*1.015,r*.96,.16,paint)
        box('Collar stem',(0,-r-.19,collar_z),(.25,.36,.26),paint,.045)
        box('Tripod foot',(0,-r-.39,collar_z+l*.05),(.46,.095,.71),paint,.04)
        box('Tripod foot rubber',(0,-r-.444,collar_z+l*.05),(.32,.01,.54),'Deep black',.015)
        knob=cyl('Collar locking knob',(-r-.10,0,collar_z),.11,.20,paint,'x',64,.009)
    else:
        zoom=(l*.73,l*.29) if which=='28-135' else (l*.58,l*.32)
        ring('Broad zoom grip',zoom[0],r,r*.9,zoom[1],'Focus rubber')
        if which=='28-135':
            for i in range(40):
                a=i*2*pi/40
                pad=box('Rounded zoom grip land',(0,r+.001,zoom[0]),(.089,.025,zoom[1]*.90),'Focus rubber',.012)
                pad.matrix_world=Matrix.Rotation(a,4,'Z')@pad.matrix_world
        else:radial_ribs('Zoom grip fine ribs',zoom[0],r,zoom[1]*.92,160)
        if which=='28-135':
            ring('Manual focus grip',l*.48,r*.974,r*.88,l*.11,'Focus rubber');radial_ribs('Fine focus ribs',l*.48,r*.975,l*.10,144)
            ring('Ultrasonic gold line',l*.915,r*.978,r*.94,.018,'Gold engraving')
        if which=='35':ring('Tamron accent ring',.24,r*.86,r*.82,.016,'Machined metal')
    for z in [l*.68,l*.9,l-.04]:ring('Machined barrel joint',z,r*.977,r*.954,.012,'Anodized black')
    # Recessed distance-scale window and fine barrel lettering.
    wz=l*.20 if not white else l*.57
    window_start=len(OBJECTS)
    box('Distance scale frame',(0,0,.007),(.42,.19,.024),'Anodized black',.024)
    box('Distance scale glass',(0,0,.020),(.35,.13,.008),'Inactive display glass',.016)
    text('Distance marks','1  3  5  ∞',(0,-.014,.025),.044)
    text('Distance units','m     ft',(0,.042,.026),.03,'Green ink')
    for o in OBJECTS[window_start:]:
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if 'frame' in o.name or 'glass' in o.name:
            import bmesh
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=12,use_grid_fill=True);bm.to_mesh(o.data);bm.free()
        for v in o.data.vertices:
            u,vv,d=v.co;angle=u/(r*.97);rr=r*.97+d
            v.co=(rr*sin(angle),rr*cos(angle),wz-vv)
        o.data.update()
    for i,number in enumerate(['28','35','50','70','100','135'] if which=='28-135' else ['70','100','135','200'] if white else [range_]):
        a=pi/2+(i-2)*.18;z=l*.31 if which=='28-135' else l*(.225 if which=='70-200-f4' else .27) if white else l*.66
        o=text('Focal length scale',number,(r*.985*cos(a),r*.985*sin(a),z),.055,'White ink' if not white else 'Deep black',rotation=(pi/2,0,0))
        o.rotation_euler=(pi/2,pi/2-a,0)
    # Mold the entire control recess onto the barrel, including its lettering.
    # A tangent rectangle leaves its corners floating visibly above the cylinder.
    if which=='28-135':
        # Cut a shallow curved pocket into the barrel before seating its insert.
        cutter=box('Switch pocket cutter',(0,0,-.003),(.375,.91,.080),None,.026)
        active(cutter);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        import bmesh
        bm=bmesh.new();bm.from_mesh(cutter.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=16,use_grid_fill=True);bm.to_mesh(cutter.data);bm.free()
        for v in cutter.data.vertices:
            u,vv,d=v.co;angle=vv/(r*.97);rr=r*.97+d
            v.co=(-rr*cos(angle),rr*sin(angle),l*.25+u)
        cutter.data.update()
        cut=housing.modifiers.new('Recessed AF IS control pocket','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=cutter;apply(housing,cut)
        OBJECTS.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
    startSwitch=len(OBJECTS)
    f4=which=='70-200-f4'
    box('AF IS switch panel',(0,0,0 if white else -.011),(.40,1.40,.026) if white else (.345,.87,.026),'White enamel' if white else 'Graphite polymer',.027)
    items=[('AF  MF',.25),('STABILIZER\nON  OFF',-.13)] if which not in ['50','35'] else [('AF  MF',0)]
    if white:items=[('1.2m-∞  3m-∞' if f4 else '1.4m-∞  2.5m-∞',.49),('AF  MF',.16),('STABILIZER\nON  OFF',-.16),('STABILIZER MODE\n1   2',-.51)]
    for label_,y in items:
        text('Switch legend',label_,(0,y+.084,.018 if white else .008),.033 if white else .041,'Deep black' if white else 'White ink')
        box('Switch slot',(0,y-.007,.025 if white else .011),(.16,.043,.024) if white else (.235,.103,.018),'Deep black',.013 if white else .040)
        box('Switch slider',(-.043,y-.007,.045 if white else .027),(.061,.041,.020) if white else (.103,.075,.020),'White enamel' if white else 'Graphite polymer',.007 if white else .023)
        for j in range(3):box('Slider knurl',(-.060+j*.016,y-.007,.058 if white else .039),(.005,.028,.004),'White enamel' if white else 'Graphite polymer',.001)
    if not white:
        box('AF IS slider position mark',(-.043,-.137,.040),(.008,.043,.003),'White ink',.001)
        screw((0,-.373,.007),r=.026)
    for o in OBJECTS[startSwitch:]:
        # Subdivide long panel edges before bending, so the inset follows the
        # cylinder at its center as well as at all four corners.
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if 'panel' in o.name:
            import bmesh
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=12,use_grid_fill=True);bm.to_mesh(o.data);bm.free()
        for v in o.data.vertices:
            u,vv,depth=v.co;angle=vv/(r*.97);radius=r*.97+depth-.008
            v.co=(-radius*cos(angle),radius*sin(angle),l*(.575 if white else .25)+u)
        o.data.update()
    mark_start=len(OBJECTS)
    brand=text('Lens side brand','Canon' if which!='35' else 'TAMRON',(-r*.97,-.13,l*(.90 if which=='70-200-f28' else .14)),.082,font='Canon' if which!='35' else 'Bold',rotation=(0,-pi/2,pi/2),mat='Deep black' if white else 'White ink')
    if which=='70-200-f28':text('Telephoto USM inscription','ULTRASONIC',(-r*.97,.11,l*.90),.045,'Red lacquer',rotation=(0,-pi/2,pi/2))
    if which=='28-135':text('USM inscription','ULTRASONIC',(-r*.97,.10,l*.91),.045,'Gold engraving',rotation=(0,-pi/2,pi/2))
    for o in OBJECTS[mark_start:]:
        o.matrix_world=Matrix.Translation(o.location)@Matrix.Rotation(-pi/2,4,'Y')@Matrix.Rotation(pi/2,4,'Z')
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        for v in o.data.vertices:
            x,y,z=v.co;radius=(r*.97 if z>=.265 else r*.82)+.002;length=math.hypot(x,y)
            v.co.x=x/length*radius;v.co.y=y/length*radius
    # Internal baffles recede toward the iris; glass elements have curved surfaces.
    ring('Front rim',l-.032,r,r*.845,.10,'Anodized black')
    ring('Front printed ring',l+.009,r*.958,r*.801,.016,'Graphite polymer')
    if white:ring('Front internal black sleeve',l-.058,r*.842,r*.778,.144,'Anodized black')
    for j in range(8):ring('Filter thread',l-.03-j*.008,r*.846,r*.825,.004,'Anodized black')
    for j in range(0 if which=='28-135' else 3):ring('Optical light baffle',l-.15-j*.13,r*(.80-j*.07),r*(.787-j*.07),.009,'Deep black')
    if which=='28-135':
        # The reference shows fine annular cuts in a shallow black recess.
        # Cut them into one surface so the grooves do not become stacked rings.
        n=256;rows=96;verts=[];faces=[]
        for row in range(rows+1):
            t=row/rows;rr=r*(.801-.396*t)
            groove=.0035*(.5-.5*cos(t*2*pi*12))
            zz=l-.180-.140*t-groove
            verts.extend((rr*cos(i*2*pi/n),rr*sin(i*2*pi/n),zz) for i in range(n))
        for row in range(rows):
            for i in range(n):
                j=(i+1)%n;a=row*n;b=(row+1)*n;faces.append((a+i,a+j,b+j,b+i))
        mesh=bpy.data.meshes.new('Shallow optical recess');mesh.from_pydata(verts,[],faces);mesh.update()
        o=bpy.data.objects.new('Shallow optical recess',mesh);scene.collection.objects.link(o);register(o,'Shallow optical recess','Machined optical baffles')
        for face in mesh.polygons:face.use_smooth=True
        uv=mesh.uv_layers.new(name='OpticalRecess');o['preserve_uv']=True
        for index,face in enumerate(mesh.polygons):
            row,i=divmod(index,n)
            coords=[(i/n,row/rows),((i+1)/n,row/rows),((i+1)/n,(row+1)/rows),(i/n,(row+1)/rows)]
            for loop,coord in zip(face.loop_indices,coords):uv.data[loop].uv=coord
        ring('Inner group retaining ring',l-.39,r*.46,r*.405,.033,'Optical barrel flocking')
    aperture_z=l*.46 if white else l-.90;outer=r*(.49 if white else .43);inner=r*(.24 if which=='70-200-f4' else .28 if white else .16)
    ring('Aperture housing',aperture_z,outer,outer*.94 if white else inner,.012,'Anodized black' if white else 'Optical barrel flocking')
    blade_count=8 if white else 6
    for i in range(blade_count):
        a=i*2*pi/blade_count;step=2*pi/blade_count
        # Nearly coplanar blades fill the complete annulus. The former zoom
        # quadrilaterals left large wedge-shaped gaps above the aperture housing.
        pts=[]
        for j in range(13):
            t=j/12;angle=a+step*t;rr=inner*(1+.025*sin(pi*t)**2)
            pts.append((rr*cos(angle),rr*sin(angle),aperture_z+.008+i*.00015))
        for j in range(12,-1,-1):
            angle=a+step*j/12;pts.append((outer*cos(angle),outer*sin(angle),aperture_z+.008+i*.00015))
        mesh=bpy.data.meshes.new('Iris blade');mesh.from_pydata(pts,[],[tuple(range(len(pts)))]);o=bpy.data.objects.new('Iris blade',mesh);scene.collection.objects.link(o);register(o,'Aperture blade','Blackened aperture steel')
    if white or which=='28-135':
        # Dark continuous barrel wall follows the optical train. The 28–135
        # previously left an open annulus exposing the exterior taper from inside.
        n=192;verts=[];faces=[]
        lining_rows=[(r*.782,l-.17),(outer,aperture_z+.025)] if white else [(r*.405,l-.32),(outer,aperture_z+.006)]
        for rr,zz in lining_rows:verts.extend((rr*cos(i*2*pi/n),rr*sin(i*2*pi/n),zz) for i in range(n))
        for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
        lining_name='Telephoto optical lining' if white else 'Zoom inner optical chamber'
        mesh=bpy.data.meshes.new(lining_name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(lining_name,mesh);scene.collection.objects.link(o);register(o,lining_name,'Optical barrel flocking')
        uv=mesh.uv_layers.new(name='OpticalRecess');o['preserve_uv']=True
        for i,face in enumerate(mesh.polygons):
            face.use_smooth=True
            for loop,coord in zip(face.loop_indices,[(i/n,0),((i+1)/n,0),((i+1)/n,1),(i/n,1)]):uv.data[loop].uv=coord
    optical_element('Optical front element',l-(.145 if which=='28-135' else .085),r*.799,.10 if which=='28-135' else .026,.038)
    optical_element('Optical inner element',l-.43 if which=='28-135' else l*.87,r*(.407 if which=='28-135' else .74),.021,.029,'Inner optical glass')
    if white:optical_element('Optical middle element',l*.58,r*.43,.014,.03,'Inner optical glass')
    optical_element('Optical rear element',l-.68 if which=='28-135' else l*.13,r*(.32 if which=='28-135' else .38),.019,.032,'Inner optical glass')
    if which=='28-135':
        arc_text('CANON ZOOM LENS EF 28-135mm 1:3.5-5.6 IS',l+.021,r*.89,.062,start=.30,span=3.85)
        arc_text('CANON INC.',l+.021,r*.89,.059,start=pi*1.05,span=.69)
        arc_text('Ø72mm',l+.021,r*.89,.065,start=pi*.60,span=.30)
    else:
        arc_text(('CANON ZOOM LENS EF ' if which not in ['35','50'] else 'TAMRON SP ' if which=='35' else 'CANON LENS EF ')+range_+' '+aperture,l+.021,r*.889,.049 if white else .046)
        arc_text('LENS MADE IN JAPAN   Ø'+str(thread)+'mm',l+.021,r*.886,.035,start=-pi*.91,span=pi*.82)
    # Tiny mount contacts and red alignment pip stay visible during lens swapping.
    for i in range(8):
        a=pi*1.15+i*.075;cyl('Lens electrical contact',(cos(a)*.468,sin(a)*.468,.012),.013,.012,'Gold engraving',vertices=16)
    sphere('Mount alignment pip',(0,r*.89,.24),(.018,.014,.018),'Red lacquer')
    return OBJECTS[start:]

def cinema():
    global current;current='c200';start=len(OBJECTS)
    chassis_outline=[(-.96,-.96),(-.98,-.73),(-.98,.72),(-.91,1.01),(-.70,1.10),(-.52,1.11),(-.40,1.24),(-.24,1.29),(.35,1.29),(.51,1.20),(.60,1.10),(.83,1.07),(.96,.82),(.96,-.77),(.83,-.98)]
    chassis=profile('Shaped cinema chassis',chassis_outline,-1.855,.35,'Magnesium shell',.075)
    front=profile('Cinema front fascia',[(-.91,-.95),(-.94,-.72),(-.94,.66),(-.80,1.09),(-.54,1.13),(-.42,1.01),(.39,1.01),(.51,1.12),(.77,1.07),(.93,.67),(.94,-.70),(.81,-.97)],.33,.405,'Graphite polymer',.044)
    # Large circular structural casting dominates the real C200 front face.
    casting_start=len(OBJECTS)
    ring('Circular mount casting',.409,.984,.432,.115,'Crinkle painted metal')
    ring('Casting perimeter seam',.469,.945,.928,.012,'Deep black')
    ring('Inner mount casting',.465,.925,.436,.075,'Crinkle painted metal')
    for a in [pi/2,pi/6,-pi/6,-pi/2,pi*7/6,pi*5/6]:
        screw((cos(a)*.938,sin(a)*.938,.478),r=.025)
    circular_casting=set(OBJECTS[casting_start:])
    for target in [chassis,front]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.438,depth=.86,location=(0,0,.14));bore=bpy.context.object
        cut=target.modifiers.new('Open cinema mount chamber','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=bore;apply(target,cut);bpy.data.objects.remove(bore,do_unlink=True)
    profile('Canon crest',[(-.50,1.10),(-.43,1.24),(-.26,1.29),(.32,1.29),(.47,1.22),(.51,1.10),(.36,1.00),(-.36,1.00)],.35,.422,'Graphite polymer',.033)
    for x,n,label_ in [(-.60,'10','PUSH AUTO IRIS'),(.60,'11','ONE-SHOT AF')]:
        cyl('Front function bezel '+n,(x,-.88,.475),.114,.032,'Anodized black')
        sphere('Front function button '+n,(x,-.88,.499),(.087,.087,.024),'Graphite polymer')
        text('Front function number '+n,n,(x,-.88,.526),.066)
        text('Front function label '+n,label_,(x,-1.006,.443),.030)
    cyl('VIDEO terminal surround',(-.73,.92,.425),.189,.05,'Deep black')
    cyl('VIDEO terminal cap',(-.73,.92,.456),.169,.027,'Graphite polymer')
    text('VIDEO terminal label','VIDEO',(-.73,.92,.477),.049)
    box('Cinema front badge',(.68,.91,.439),(.145,.168,.018),'Red lacquer',.012)
    text('Cinema front C','C',(.68,.91,.451),.133,font='Canon')
    box('Base rail',(0,-.99,-.65),(1.97,.11,2.33),'Anodized black',.055)
    mountStart=len(OBJECTS)
    mount(.48,cinema=True)
    mount_objects=set(OBJECTS[mountStart:])
    text('Front Canon','Canon',(0,1.135,.429),.18,font='Canon');text('Front EOS','EOS',(.68,1.061,.441),.065)
    # Left-side operator panel, placed using the C200 reference layout.
    panelStart=len(OBJECTS)
    profile('Side fascia',[(-1,-1.01),(-1,.71),(-.92,.98),(.83,.98),(.96,.82),(1,-.72),(.89,-1.01)],-.035,.035,'Graphite polymer',.055)
    # The operator controls sit in a stepped casting. The vent is a continuous
    # dark opening with horizontal louvers, not individual painted stripes.
    profile('Operator panel surround',[(-.92,-.82),(-.92,.28),(.27,.28),(.36,.19),(.36,-.79),(.25,-.85)],.036,.062,'Deep black',.025)
    profile('Operator control casting',[(-.85,-.77),(-.85,-.16),(-.70,-.16),(-.70,.18),(-.54,.25),(.12,.25),(.18,.15),(.18,-.73),(.05,-.80)],.062,.077,'Crinkle painted metal',.033)
    box('Exhaust opening',(.29,-.29,.068),(.17,1.03,.019),'Deep black',.028)
    for i in range(14):box('Exhaust louver',(.29,-.76+i*.071,.085),(.18,.027,.029),'Graphite polymer',.007)
    box('CFast door seam',(.68,-.15,.058),(.49,1.04,.025),'Deep black',.032)
    box('CFast door',(.68,-.15,.078),(.46,1.01,.028),'Graphite polymer',.027)
    box('CFast finger recess',(.65,.16,.095),(.13,.18,.011),'Deep black',.025)
    box('CFast finger pad',(.65,.16,.101),(.105,.152,.012),'Graphite polymer',.019)
    box('CFast door latch',(.74,-.74,.080),(.17,.11,.027),'Anodized black',.012)
    for i in range(6):box('CFast latch rib',(.68+i*.021,-.727,.097),(.007,.027,.008),'Graphite polymer',.002)
    text('CFast label','CFast',(.50,-.70,.092),.049)
    cyl('Power control',(-.12,.64,.074),.139,.06,'Anodized black')
    tab=box('Power lever',(-.12,.64,.114),(.24,.034,.035),'Graphite polymer',.012);tab.rotation_euler.z=.15
    text('Power label','POWER',(-.22,.875,.069),.067)
    for y,t in [(.765,'CAMERA'),(.60,'OFF'),(.45,'MEDIA')]:text('Power legend',t,(-.51,y,.07),.041)
    text('Canon side wordmark','Canon',(.58,.55,.071),.13,font='Canon')
    text('4K mark','4K',(-.66,.29,.071),.135)
    for x,y,label_,n in [(-.48,.03,'MAGN.','1'),(-.48,-.23,'PEAKING','2'),(-.48,-.47,'ZEBRA','3'),(-.48,-.71,'WFM','4'),(-.02,-.06,'ISO/GAIN','5'),(-.02,-.37,'SHUTTER','6'),(-.02,-.69,'DISP.','7'),(-.80,-.24,'ND FILTER','+'),(-.80,-.51,'','−')]:
        cyl('Function bezel',(x,y,.075),.071,.024,'Deep black');sphere('Function button',(x,y,.098),(.057,.057,.018),'Anodized black');text('Function number',n,(x,y,.117),.062);text('Function label',label_,(x,y+.105,.087),.042)
    cyl('Record bezel',(-.43,-.92,.10),.109,.044,'Anodized black');sphere('Red REC button',(-.43,-.92,.129),(.072,.072,.023),'Red lacquer');text('REC label','REC',(-.26,-.82,.116),.046)
    box('Control dial recess',(-.77,-.91,.062),(.20,.22,.032),'Deep black',.027)
    dial((-.77,-.91,.082),.098,'y',width=.071)
    for x in [.02,.20]:cyl('Playback button',(x,-.91,.09),.056,.039,'Anodized black')
    text('Camera model','EOS\nC200',(.54,-.83,.107),.077)
    box('Cinema EOS badge',(.84,-.84,.092),(.17,.19,.029),'Red lacquer',.022);text('Cinema mark','C',(.84,-.84,.111),.155,font='Canon')
    for p in [(-.87,.79,.057),(-.90,-.92,.068),(.83,.23,.09),(.82,-.98,.07)]:screw(p,r=.021)
    tr=Matrix.Translation(Vector((.982,.06,-.73)))@Matrix.Rotation(pi/2,4,'Y')
    for o in OBJECTS[panelStart:]:o.matrix_world=tr@o.matrix_world
    # Right ergonomic handgrip, battery compartment and viewfinder.
    rightStart=len(OBJECTS)
    profile('Right side service cover',[(-1.02,-.94),(-1.02,.83),(-.85,.98),(.72,.98),(.95,.76),(.98,-.90)],-.01,.022,'Graphite polymer',.055)
    box('Intake vent well',(-.73,-.08,.029),(.19,1.13,.026),'Deep black',.025)
    for i in range(16):box('Air intake louver',(-.73,-.59+i*.067,.050),(.18,.025,.021),'Graphite polymer',.005)
    text('Intake marking','AIR INTAKE',(-.55,-.24,.041),.034,rotation=(0,0,pi/2))
    for y,label_ in [(.71,'INPUT 1'),(.39,'INPUT 2')]:
        box('Audio input selector panel',(-.59,y,.050),(.44,.28,.034),'Anodized black',.017)
        text('Audio input label',label_,(-.60,y+.10,.071),.028)
        for dy,legend in [(.015,'ANALOG'),(-.075,'LINE  MIC +48V')]:
            box('Audio selector track',(-.66,y+dy,.071),(.16,.040,.018),'Deep black',.005)
            box('Audio selector tab',(-.67,y+dy,.084),(.044,.032,.019),'Graphite polymer',.004)
            text('Audio selector legend',legend,(-.46,y+dy,.074),.017)
    for x,y in [(-.91,.85),(.76,.73),(.79,-.75)]:screw((x,y,.037),r=.019)
    tr=Matrix.Translation(Vector((-.97,.04,-.73)))@Matrix.Rotation(-pi/2,4,'Y')
    for o in OBJECTS[rightStart:]:o.matrix_world=tr@o.matrix_world
    gripStart=len(OBJECTS)
    # Local X runs toward the lens, local Z is the grip's outer face.
    cyl('Grip rosette seat',(0,.10,.015),.23,.085,'Anodized black')
    dial((0,.10,.082),.24,'z',width=.085)
    profile('GR-V1 grip shell',[(-.58,.14),(-.48,.35),(-.22,.40),(.34,.30),(.52,.13),(.48,-.26),(.29,-.42),(-.23,-.45),(-.51,-.27)],.13,.40,'Graphite polymer',.10)
    profile('Grip rubber overmold',[(-.25,.30),(.30,.24),(.44,.10),(.42,-.23),(.24,-.34),(-.22,-.36),(-.36,-.20)],.393,.411,'Pebbled rubber',.038)
    profile('Grip rear control panel',[(-.54,.12),(-.44,.29),(-.30,.27),(-.25,.07),(-.33,-.20),(-.49,-.21)],.402,.433,'Graphite polymer',.035)
    cyl('Grip record recess',(-.43,-.10,.449),.073,.029,'Deep black')
    cyl('Grip record button',(-.43,-.10,.469),.050,.021,'Anodized black')
    cyl('Grip record red pip',(-.43,-.10,.482),.014,.003,'Red lacquer',vertices=24)
    dial((-.35,.15,.445),.078,'y',width=.095)
    text('Grip start stop','START\nSTOP',(-.54,-.10,.44),.023)
    # Strap bridges the hand space; its padded center is distinct from the webs.
    for x in [-.46,.44]:
        box('Strap attachment',(x,.10,.443),(.10,.28,.054),'Anodized black',.015)
        box('Strap web',(x,.10,.49),(.22,.19,.034),'Focus rubber',.018)
    profile('Padded Canon hand strap',[(-.45,-.04),(-.36,-.11),(.28,-.11),(.43,-.04),(.40,.23),(.25,.30),(-.32,.30),(-.46,.22)],.52,.58,'Pebbled rubber',.040)
    text('Hand strap Canon','Canon',(-.02,.10,.587),.087,font='Canon')
    for y in [-.065,.252]:
        for i in range(24):line('Strap stitching',[(-.32+i*.027,y,.587),(-.307+i*.027,y,.587)],.0015,'Graphite polymer')
    box('Strap adjustment buckle',(.26,.12,.606),(.18,.23,.032),'Anodized black',.015)
    box('Buckle web',(.26,.12,.625),(.095,.25,.012),'Focus rubber',.006)
    tr=Matrix.Translation(Vector((-.96,-.15,-.45)))@Matrix.Rotation(-pi/2,4,'Y')
    for o in OBJECTS[gripStart:]:o.matrix_world=tr@o.matrix_world
    rearStart=len(OBJECTS)
    box('Rear control fascia',(0,.02,0),(1.77,1.91,.07),'Graphite polymer',.07)
    box('Battery bay',(-.23,-.60,.042),(1.19,.68,.035),'Deep black',.045)
    box('BP-A30 battery',(-.23,-.59,.16),(1.05,.57,.25),'Anodized black',.055)
    box('Battery label',(-.23,-.59,.289),(.86,.40,.006),'Graphite polymer',.018)
    text('Battery Canon','Canon',(-.23,-.48,.295),.064,font='Canon')
    box('Battery white identification strip',(-.23,-.738,.296),(.84,.104,.006),'White ink',.007)
    text('Battery model','BP-A30',(-.47,-.738,.301),.055,'Deep black')
    text('Battery chemistry','Intelligent Li-ion Battery',(-.075,-.738,.301),.020,'Deep black')
    for i in range(5):cyl('Battery charge indicator',(-.46+i*.068,-.590,.296),.009,.004,'Graphite polymer',vertices=24,bevel=.001)
    text('Battery charge zero','0',(-.55,-.590,.299),.028)
    text('Battery charge full','100%',(-.115,-.590,.299),.026)
    cyl('Battery check membrane',(.070,-.61,.296),.052,.008,'Graphite polymer',vertices=64,bevel=.002)
    ring('Battery check outline',.301,.051,.047,.002,'White ink',center=(.07,-.61))
    text('Battery check legend','CHECK',(.070,-.535,.300),.025)
    box('Battery release recess',(.398,-.425,.067),(.105,.22,.040),'Deep black',.024)
    box('Battery release tab',(.405,-.415,.095),(.068,.129,.029),'Graphite polymer',.016)
    text('Battery release legend','BATTERY\nRELEASE',(.388,-.261,.070),.026)
    for x in [-.20,.12]:
        box('SD card slot frame',(x,.22,.052),(.23,.67,.039),'Deep black',.025)
        box('SD card door',(x,.22,.082),(.19,.61,.033),'Graphite polymer',.021)
        box('SD door thumb pad',(x,.37,.104),(.17,.24,.012),'Anodized black',.013)
        box('SD door bottom grip',(x,-.04,.104),(.15,.032,.015),'Anodized black',.008)
    text('SD card legend','SD CARD',(-.04,.62,.065),.049)
    text('SD slots','A             B',(-.04,-.15,.065),.039)
    cyl('Slot select',(-.04,-.23,.073),.048,.029,'Anodized black')
    text('Slot select label','SLOT SELECT',(-.04,-.30,.069),.029)
    box('Audio control cover',(-.54,.19,.058),(.30,.74,.038),'Anodized black',.018)
    for y,channel in [(.34,'CH1'),(.04,'CH2')]:
        dial((-.54,y,.10),.091,'z',width=.031)
        text('Audio channel',channel,(-.53,y+.12,.084),.034)
        text('Audio dial scale','0 . 5 . 10',(-.54,y,.125),.025)
    for y,label_ in [(.62,'FUNC'),(.36,'CANCEL'),(.08,'MENU')]:
        cyl('Rear navigation button',(-.79,y,.072),.049,.024,'Anodized black')
        text('Rear navigation label',label_,(-.79,y+.088,.061),.027)
    # Closed connector covers follow the photographed rear terminal column.
    for y,label_ in [(.84,'INPUT 1'),(.47,'INPUT 2')]:
        box('XLR socket housing',(.58,y,.077),(.46,.34,.105),'Graphite polymer',.036)
        ring('XLR socket metal rim',.144,.128,.115,.016,'Machined metal',center=(.57,y))
        cyl('XLR dust cap',(.57,y,.16),.114,.027,'Focus rubber')
        box('XLR release',(.79,y,.15),(.045,.14,.025),'White ink',.005)
        text('XLR release legend','PUSH',(.792,y,.166),.023,'Graphite polymer',rotation=(0,0,pi/2))
        for xx,yy in [(.407,y-.118),(.722,y+.118)]:screw((xx,yy,.138),r=.018)
        text('XLR label',label_,(.56,y+.14,.137),.031)
    for y,h,label_ in [(.10,.26,'SDI'),(-.18,.23,'USB / PHONES'),(-.48,.33,'LAN'),(-.81,.25,'DC IN\n16.7V')]:
        box('Terminal cover '+label_,(.58,y,.068),(.43,h,.072),'Graphite polymer',.023)
        if label_=='SDI':cyl('SDI connector cap',(.58,y,.126),.082,.058,'Focus rubber')
        if label_=='USB / PHONES':
            # Molded headphone and USB symbols shown on the closed connector flap.
            line('Headphone arch',[(.476+.041*cos(a),y+.005+.045*sin(a),.108) for a in np.linspace(0,pi,17)],.004,'White ink')
            for xx in [.435,.517]:box('Headphone ear',(xx,y-.019,.108),(.012,.038,.003),'White ink',.003)
            line('USB connector stem',[(.595,y,.108),(.715,y,.108)],.004,'White ink')
            line('USB branch upper',[(.632,y,.108),(.656,y+.030,.108),(.685,y+.030,.108)],.003,'White ink')
            line('USB branch lower',[(.643,y,.108),(.665,y-.030,.108),(.691,y-.030,.108)],.003,'White ink')
            line('USB arrow',[(.702,y+.010,.108),(.716,y,.108),(.702,y-.010,.108)],.003,'White ink')
        elif label_=='LAN':
            for xx,yy in [(.58,y+.040),(.532,y-.037),(.628,y-.037)]:
                line('Network node',[(xx-.025,yy-.016,.108),(xx+.025,yy-.016,.108),(xx+.025,yy+.016,.108),(xx-.025,yy+.016,.108),(xx-.025,yy-.016,.108)],.003,'White ink')
            line('Network trunk',[(.58,y+.024,.108),(.58,y,.108),(.532,y,.108),(.532,y-.021,.108)],.003,'White ink')
            line('Network branch',[(.58,y,.108),(.628,y,.108),(.628,y-.021,.108)],.003,'White ink')
        else:text('Terminal legend '+label_,label_,(.58,y,.161 if label_=='SDI' else .108),.031)
    tr=Matrix.Translation(Vector((0,0,-1.88)))@Matrix.Rotation(pi,4,'Y')
    for o in OBJECTS[rearStart:]:o.matrix_world=tr@o.matrix_world
    eye=box('Rear EVF',(.31,.92,-1.68),(.68,.48,.80),'Graphite polymer',.10);eye.rotation_euler.x=-.12
    eyecup(.31,.94,-2.08)
    box('EVF diopter recessed track',(.31,.673,-1.84),(.30,.024,.124),'Deep black',.020)
    box('EVF diopter sliding lever',(.31,.654,-1.84),(.101,.028,.086),'Graphite polymer',.014)
    for xx in [.282,.302,.322,.342]:box('EVF diopter thumb rib',(xx,.637,-1.84),(.007,.008,.070),'Focus rubber',.002)
    bare_body=[o for o in OBJECTS[start:] if o not in OBJECTS[gripStart:rearStart]]
    # Detachable handle with a hollow grip, shoe and drilled accessory holes.
    accessories_start=len(OBJECTS)
    # HDU-2 is a narrow continuous casting, not a cage plate with two posts.
    # Build its side silhouette in local XY, then turn local X along camera Z.
    handle=profile('HDU-2 continuous casting',[(-1.49,1.15),(-1.57,1.27),(-1.57,1.88),(-1.46,2.00),(.30,2.00),(.44,1.87),(.44,1.31),(.30,1.15)],-.235,.235,'Crinkle painted metal',.043)
    opening=profile('Handle opening cutter',[(-1.28,1.39),(-1.28,1.70),(-1.21,1.79),(-1.05,1.80),(-.96,1.76),(-.86,1.80),(-.69,1.80),(-.60,1.76),(-.50,1.80),(-.33,1.80),(-.24,1.76),(-.14,1.80),(.06,1.80),(.15,1.69),(.15,1.43),(.03,1.32),(-1.11,1.32)],-.40,.40,'Deep black',.025)
    cut=handle.modifiers.new('Open hand clearance','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=opening;apply(handle,cut);OBJECTS.remove(opening);bpy.data.objects.remove(opening,do_unlink=True)
    if handle.ray_cast(Vector((-.65,1.55,.60)),Vector((0,0,-1)),distance=1.2)[0]:raise RuntimeError('HDU-2 hand opening is obstructed')
    finish(handle,.010,3)
    handle.rotation_euler.y=-pi/2
    # The pair of transverse sockets are real bores through the front upright.
    for y in [1.39,1.84]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.067,depth=.72,location=(0,y,.305),rotation=(0,pi/2,0));bore=bpy.context.object
        cut=handle.modifiers.new('Accessory socket','BOOLEAN');cut.operation='DIFFERENCE';cut.solver='EXACT';cut.object=bore;apply(handle,cut);bpy.data.objects.remove(bore,do_unlink=True)
        for side in [-1,1]:
            socket=ring('Handle socket liner',0,.092,.067,.024,'Anodized black');socket.rotation_euler.y=pi/2;socket.location=(side*.243,y,.305)
    box('Handle top mounting insert',(0,2.008,-.69),(.36,.015,1.10),'Anodized black',.025)
    for z in [-1.04,-.61]:
        cyl('Handle top threaded well',(0,2.018,z),.046,.005,'Deep black','y',48,.001)
        for x in [-.074,.074]:
            screw_start=len(OBJECTS);screw((0,0,0),r=.013)
            for o in OBJECTS[screw_start:]:o.matrix_world=Matrix.Translation(Vector((x,2.020,z)))@Matrix.Rotation(-pi/2,4,'X')@o.matrix_world
    # Cold shoe rails near the front of the carrying surface.
    box('Handle cold shoe seat',(0,2.018,-.13),(.36,.024,.35),'Anodized black',.013)
    for x in [-.16,.16]:
        box('Handle cold shoe rail',(x,2.046,-.13),(.045,.043,.33),'Machined metal',.005)
        box('Handle cold shoe return',(x+(.014 if x<0 else -.014),2.067,-.13),(.047,.012,.33),'Machined metal',.003)
    cyl('Handle mounting wheel',(0,1.36,-.69),.20,.071,'Anodized black','y',96,.012)
    knob_start=len(OBJECTS);radial_ribs('Mounting wheel knurl',0,.199,.047,80)
    for o in OBJECTS[knob_start:]:o.matrix_world=Matrix.Translation(Vector((0,1.36,-.69)))@Matrix.Rotation(-pi/2,4,'X')@o.matrix_world
    cyl('Mounting wheel socket',(0,1.399,-.69),.038,.004,'Deep black','y',6,.001)
    for side in [-1,1]:
        for y,z in [(1.27,-1.34),(1.85,-1.34),(1.25,.29),(1.66,.34)]:
            screw_start=len(OBJECTS);screw((0,0,0),r=.020)
            for o in OBJECTS[screw_start:]:o.matrix_world=Matrix.Translation(Vector((side*.239,y,z)))@Matrix.Rotation(side*pi/2,4,'Y')@o.matrix_world
    # Monitor on the articulated mounting arm. Details exist on both faces.
    cyl('Monitor arm side attachment',(.31,1.84,.305),.088,.18,'Anodized black','x',64)
    box('Monitor articulated arm',(.43,2.005,.305),(.14,.38,.16),'Graphite polymer',.032)
    cyl('Monitor hinge',(.55,2.15,.305),.13,.30,'Anodized black','x',64)
    monitorStart=len(OBJECTS)
    box('LM-V1 monitor',(0,0,0),(1.62,.96,.15),'Graphite polymer',.055)
    box('Monitor display bezel',(.100,0,.080),(1.31,.836,.022),'Deep black',.025)
    box('Monitor glass',(.100,0,.094),(1.22,.730,.010),'Inactive display glass',.020)
    # LM-V1 front controls from Canon's C200 manual, page 17.
    for yy,name in [(.345,'FUNC'),(.211,'MENU'),(-.083,'MIRROR'),(-.218,'CANCEL'),(-.353,'DISP')]:
        cyl('Monitor '+name+' bezel',(-.674,yy,.084),.055,.018,'Deep black',vertices=48,bevel=.003)
        sphere('Monitor '+name+' button',(-.674,yy,.100),(.044,.044,.012),'Graphite polymer')
        text('Monitor '+name+' legend',name,(-.674,yy+.067,.084),.024)
    cyl('Monitor joystick recess',(-.674,.063,.085),.062,.020,'Deep black',vertices=64,bevel=.004)
    sphere('Monitor joystick',(-.674,.063,.106),(.040,.040,.025),'Focus rubber')
    ring('Monitor joystick ring',.108,.059,.049,.008,'Graphite polymer',center=(-.674,.063))
    for x in [-.61,.61]:screw((x,.32,-.080),r=.018)
    # Bottom mounting socket and video connector occupy separate positions.
    mount_ring=ring('Monitor mounting socket',0,.052,.035,.018,'Machined metal');mount_ring.rotation_euler.x=pi/2;mount_ring.location=(.13,-.475,0)
    video=cyl('Monitor video connector',(-.60,-.464,-.025),.047,.035,'Anodized black','y',48)
    tr=Matrix.Translation(Vector((.54,2.57,.305)))@Matrix.Rotation(pi-.16,4,'Y')
    for o in OBJECTS[monitorStart:]:o.matrix_world=tr@o.matrix_world
    # Short monitor cable with plugs.
    line('Monitor cable',[(1.128,2.106,.425),(1.28,2.08,.44),(1.38,1.84,.31),(1.29,1.19,-.22),(.99,.76,-.46)],.024,'Focus rubber')
    cyl('Monitor cable connector',(.99,.76,-.46),.049,.09,'Anodized black','x',48)
    for o in OBJECTS[accessories_start:]:o.location.y+=.16
    # Lens dimensions establish 55 mm per scene unit (28-135: 96.8 mm length).
    # Calibrate the bare body independently of the detachable grip and monitor.
    bpy.context.view_layer.update()
    corners=[o.matrix_world@Vector(c) for o in bare_body for c in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in corners) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in corners) for i in range(3)))
    target=Vector((144/55,153/55,179/55))
    factors=Vector(tuple(target[i]/(hi[i]-lo[i]) for i in range(3)))
    # Anchor scaling at the front mating plane so every EF lens still attaches.
    pivot=Vector((0,0,hi.z))
    calibration=Matrix.Translation(pivot)@Matrix.Diagonal((*factors,1))@Matrix.Translation(-pivot)
    for o in OBJECTS[start:]:
        if o in circular_casting:
            circular=Matrix.Translation(pivot)@Matrix.Diagonal((factors.x,factors.x,factors.z,1))@Matrix.Translation(-pivot)
            o.matrix_world=circular@o.matrix_world
        elif o not in mount_objects:o.matrix_world=calibration@o.matrix_world
    print('C200 body calibration: original mm',tuple(round(v*55,2) for v in hi-lo),'target mm',(144,153,179),'scale',tuple(factors),flush=True)
    return OBJECTS[start:]

def adapter():
    global current;current='adapter';start=len(OBJECTS)
    length=24/55;radius=71.2/110
    ring('Adapter rear housing',.090,radius-.022,.43,.180,'Crinkle painted metal')
    ring('Adapter front housing',(.175+length-.008)/2,radius,.43,length-.183,'Crinkle painted metal')
    ring('Adapter rear weather seal',.008,radius-.026,.47,.016,'Focus rubber')
    # RF bayonet extends into the camera; the EF face terminates at the other
    # mating plane. Only thin metal edges remain visible with a lens attached.
    ring('Adapter RF bayonet',-.036,.535,.43,.072,'Machined metal')
    ring('Adapter EF flange',length-.007,.567,.475,.014,'Machined metal')
    ring('Adapter front polymer rim',length-.011,radius,.566,.020,'Anodized black')
    ring('Adapter rear silver trim',.042,radius-.014,.53,.049,'Machined metal')
    control_radius=74.4/110
    ring('Adapter control ring',.143,control_radius-.008,radius-.014,.139,'Anodized black')
    for zz in [.075,.211]:ring('Control ring edge',zz,control_radius-.002,control_radius-.015,.008,'Graphite polymer')
    # Five rows of diamond knurling match the control-ring version's grip.
    verts=[];faces=[];columns=160;rows=5;step=2*pi/columns
    for row in range(rows):
        zz=.089+row*.027
        for i in range(columns):
            aa=(i+(row%2)*.5)*step;k=len(verts)
            for angle,dz,rr in [(aa-step*.46,0,control_radius-.008),(aa,-.012,control_radius-.008),(aa+step*.46,0,control_radius-.008),(aa,.012,control_radius-.008),(aa,0,control_radius)]:
                verts.append((rr*cos(angle),rr*sin(angle),zz+dz))
            faces.extend((k+j,k+(j+1)%4,k+4) for j in range(4))
    mesh=bpy.data.meshes.new('Control ring diamond knurl');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Control ring diamond knurl',mesh);scene.collection.objects.link(o);register(o,'Control ring diamond knurl','Anodized black')
    detail_start=len(OBJECTS)
    text('Adapter Canon logo','Canon',(0,0,0),.071,font='Canon')
    for o in OBJECTS[detail_start:]:
        active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        for v in o.data.vertices:
            u,vv,d=v.co;angle=u/radius;rr=radius+.002+d
            v.co=(-rr*sin(angle),rr*cos(angle),.300+vv)
    label=text('Adapter name','CONTROL RING MOUNT ADAPTER EF-EOS R',(0,0,0),.024)
    active(label);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for v in label.data.vertices:
        u,vv,d=v.co;rr=radius+.002+d;angle=u/rr-1.05;v.co=(-rr*sin(angle),rr*cos(angle),.300+vv)
    box('Adapter release seat',(.638,0,.325),(.035,.19,.16),'Deep black',.025)
    box('Adapter release lever',(.661,0,.329),(.034,.125,.102),'Graphite polymer',.020)
    sphere('Adapter RF alignment mark',(-.33,.532,.075),(.011,.008,.027),'Red lacquer')
    sphere('Adapter EF alignment mark',(0,radius+.005,length-.047),(.014,.009,.014),'Red lacquer')
    return OBJECTS[start:]

def bake_occlusion(name,objects):
    # A second UV set carries local contact shadowing independently of the
    # repeating grain textures. Joining preserves material slots and UV0.
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    obj=bpy.context.object;obj.name=name+' | baked assembly'
    obj.data.uv_layers.new(name='BakedAO');obj.data.uv_layers.active_index=1
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.0,island_margin=.006);bpy.ops.object.mode_set(mode='OBJECT')
    ao_image=bpy.data.images.new(name+'-occlusion',width=2048,height=2048,alpha=False)
    ao_image.colorspace_settings.name='Non-Color'
    restores=[]
    group=bpy.data.node_groups.get('glTF Material Output') or bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
    if not group.interface.items_tree:group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
    for slot in obj.material_slots:
        if slot.material is None:continue
        mat=slot.material.copy();slot.material=mat;nodes=mat.node_tree.nodes;links=mat.node_tree.links
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        original=output.inputs['Surface'].links[0].from_socket
        ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.16;ao.samples=32
        emission=nodes.new('ShaderNodeEmission');links.new(ao.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
        tex=nodes.new('ShaderNodeTexImage');tex.image=ao_image;nodes.active=tex
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map='BakedAO';links.new(uv.outputs[0],tex.inputs['Vector'])
        gltf=nodes.new('ShaderNodeGroup');gltf.node_tree=group;links.new(tex.outputs['Color'],gltf.inputs['Occlusion'])
        restores.append((mat,output,original,ao,emission))
    scene.render.engine='CYCLES';scene.cycles.samples=32
    bpy.ops.object.bake(type='EMIT',use_clear=True,margin=8,uv_layer='BakedAO')
    for mat,output,original,ao,emission in restores:
        mat.node_tree.links.new(original,output.inputs['Surface']);mat.node_tree.nodes.remove(ao);mat.node_tree.nodes.remove(emission)
    obj.data.uv_layers.active_index=0;obj.data.uv_layers[0].active_render=True
    ao_image.filepath_raw=os.path.join(WORK,name+'-occlusion.png');ao_image.file_format='PNG';ao_image.save();ao_image.pack()
    print('BAKED AO',name,flush=True)
    return [obj]

def export_asset(name,objects):
    import bmesh
    # Smart UVs provide real material-space grain; normals are corrected before export.
    for o in objects:
        if o.type!='MESH':continue
        active(o)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        if len(o.data.polygons)>0 and not o.get('preserve_uv'):
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
        if o.data.materials and any(finish in o.data.materials[0].name for finish in ['Scanned grip rubber','Crinkle painted metal']):
            # Smart projection packs each part independently. Normalize density
            # so a small thumb pad does not have larger grain than the hand grip.
            transform=o.matrix_world.to_3x3();normal_transform=transform.inverted().transposed()
            world_area=abs(transform.determinant())*sum(face.area*(normal_transform@face.normal).length for face in o.data.polygons)
            uv=o.data.uv_layers.active.data;uv_area=0
            for face in o.data.polygons:
                points=[uv[i].uv for i in face.loop_indices]
                uv_area+=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(points,points[1:]+points[:1])))*.5
            if uv_area<1e-9:raise RuntimeError('Textured finish has no usable surface UVs: '+o.name)
            density=math.sqrt(world_area/uv_area)/1.4
            for loop in uv:loop.uv*=density
    # Merge by material so detailed geometry remains inexpensive to draw in WebGL.
    grouped={}
    for o in objects:
        if o.type=='MESH' and len(o.data.polygons):grouped.setdefault(o.data.materials[0].name,[]).append(o)
    joined=[]
    for mat,items in grouped.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in items:o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name+' | '+mat;joined.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for o in joined:o.select_set(True)
    if name in ['r7','40d','c200']:joined=bake_occlusion(name,joined)
    filepath=os.path.join(OUT,name+'.glb')
    bpy.ops.export_scene.gltf(filepath=filepath,export_format='GLB',use_selection=True,export_yup=False,export_apply=True,export_cameras=False,export_lights=False,export_materials='EXPORT',export_animations=False)
    print('EXPORTED',name,os.path.getsize(filepath),sum(len(o.data.polygons) for o in joined),flush=True)
    return joined

if __name__=='__main__':
    targets=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['r7','40d','c200','28-135','70-200-f4','70-200-f28','35','50','adapter']
    for name in targets:
        OBJECTS=[]
        objs=body(name) if name in ['r7','40d'] else cinema() if name=='c200' else adapter() if name=='adapter' else lens(name)
        asset=export_asset(name,objs)
        # Keep one editable project per asset without the other configurations.
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORK,name+'.blend'))
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
