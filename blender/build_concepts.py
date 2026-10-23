# Copyright (C) 2026 Jonathan Mann
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build Song A Day industrial-design studies with Blender 4.5+.

Usage: blender -b --python blender/build_concepts.py -- --out renders --samples 48
Units are metres. These are visual envelope studies, not fabrication CAD.
Code: GPL-3.0-or-later. Original geometry and illustrative screen art: CC BY 4.0.
"""
import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument('--out', default='renders')
ap.add_argument('--samples', type=int, default=48)
ap.add_argument('--resolution', type=int, default=1500)
ap.add_argument('--only', default='')
ap.add_argument('--no-render', action='store_true')
args = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUT = Path(args.out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
MM = .001

bpy.ops.wm.read_factory_settings(use_empty=True)


def rgb(h):
    h = h.lstrip('#')
    v = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c < .04045 else ((c + .055) / 1.055) ** 2.4 for c in v)


def mat(name, color, rough=.4, metal=0, texture=False):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb(color), 1)
    m.use_nodes = True
    n = m.node_tree.nodes
    p = n.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb(color), 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if texture:
        tc = n.new('ShaderNodeTexNoise')
        tc.inputs['Scale'].default_value = 210
        tc.inputs['Detail'].default_value = 2
        bump = n.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .13
        bump.inputs['Distance'].default_value = .00012
        m.node_tree.links.new(tc.outputs['Fac'], bump.inputs['Height'])
        m.node_tree.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m


ink = mat('Graphite | fine mineral texture', '#23282a', .48, .03, True)
black = mat('Carbon | fine matte ABS', '#111517', .38, .02, True)
ivory = mat('Bone | unpainted textured ABS', '#e8dec8', .5, 0, True)
terra = mat('Oxide | textured ABS, ceramic appearance', '#a24f36', .53, 0, True)
silver = mat('Brushed aluminium accent', '#b5b6af', .3, .85)
orange = mat('Vermilion button', '#ec582e', .4)
bronze = mat('Warm nickel button', '#c4ac76', .28, .7)
dark = mat('Grille interior / rubber feet', '#080b0c', .75)
pcb = mat('PCB solder mask', '#245d50', .55)
chip = mat('IC moulding', '#212626', .6)
glass = mat('Opaque smoked screen surround', '#0c1416', .24, .05)
solar = mat('ETFE solar cell | deep indigo', '#162e48', .3, .35)
solarline = mat('Solar bus bar', '#626f82', .3, .6)
floor = mat('Warm gallery floor', '#ddd8cd', .78)
label = mat('Warm white print', '#b8c0b5', .6)

wood = mat('Walnut | procedural grain', '#67452c', .42)
n = wood.node_tree.nodes
p = n.get('Principled BSDF')
tc = n.new('ShaderNodeTexCoord')
mapping = n.new('ShaderNodeVectorMath'); mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (4, 4, 80)
noise = n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 2.2
noise.inputs['Detail'].default_value = 3
ramp = n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .2
ramp.color_ramp.elements[0].color = (*rgb('#352719'), 1)
ramp.color_ramp.elements[1].position = .8
ramp.color_ramp.elements[1].color = (*rgb('#936845'), 1)
wood.node_tree.links.new(tc.outputs['Generated'], mapping.inputs[0])
wood.node_tree.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
wood.node_tree.links.new(noise.outputs['Fac'], ramp.inputs[0])
wood.node_tree.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
bump = n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .15
bump.inputs['Distance'].default_value = .0001
wood.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
wood.node_tree.links.new(bump.outputs['Normal'], p.inputs['Normal'])


def illustrative_pixel(x, y):
    """An original singer-and-guitar study, never an actual Song A Day frame."""
    # Coordinates have their origin at the image's lower left.
    v = .12 + .12 * y / 120 + .1 * math.sin(x * .021)
    if 9 < x < 41 and 17 < y < 104: v = .23 + .05 * math.sin(x * .4)
    if 45 < x < 52 and 0 < y < 120: v = .48
    if 143 < x < 149: v = .38
    # torso and shoulder silhouette
    if ((x - 87) / 37) ** 2 + ((y - 22) / 44) ** 2 < 1: v = .31
    if 66 < x < 104 and 10 < y < 68: v = .4 + .1 * (x - 66) / 38
    # neck / ears / face
    if 78 < x < 93 and 57 < y < 78: v = .62
    if ((x - 86) / 18) ** 2 + ((y - 86) / 23) ** 2 < 1:
        v = .75 + .13 * (x - 86) / 18
    if ((x - 85) / 21) ** 2 + ((y - 94) / 18) ** 2 < 1 and y > 92: v = .25
    if ((x - 86) / 17) ** 2 + ((y - 77) / 15) ** 2 < 1 and y < 81: v = .25
    # spectacles and eyes
    if 71 < x < 99 and 87 < y < 90: v = .07
    if (((x - 77) / 7) ** 2 + ((y - 88) / 5) ** 2 < 1 or
        ((x - 94) / 6) ** 2 + ((y - 88) / 5) ** 2 < 1): v = .36
    if 85 < x < 89 and 78 < y < 90: v = .56
    if 81 < x < 91 and 73 < y < 75: v = .76
    # guitar body / neck, sound hole and strings
    a = ((x - 84) / 28) ** 2 + ((y - 23) / 18) ** 2
    b = ((x - 91) / 21) ** 2 + ((y - 40) / 15) ** 2
    if a < 1 or b < 1: v = .71 + .12 * math.sin(x * .06)
    if 91 < x < 141 and abs(y - (x * .28 + 8)) < 3: v = .59
    if ((x - 92) / 7) ** 2 + ((y - 35) / 7) ** 2 < 1: v = .08
    if 85 < x < 139 and abs(y - (x * .28 + 8)) < .55: v = .9
    # forearms and picking hand
    if 59 < x < 87 and abs(y - (71 - x * .42)) < 4: v = .77
    if 120 < x < 128 and 35 < y < 48: v = .74
    # microphone and stand in front of performer
    if 108 < x < 111 and 0 < y < 80: v = .07
    if 96 < x < 112 and 78 < y < 83: v = .1
    return max(0, min(1, v))


def screenmat(name, light, low):
    im = bpy.data.images.new(name + ' | 160 x 120 / 1 bit', width=160, height=120)
    im.colorspace_settings.name = 'Non-Color'
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    hi, lo = rgb(light), rgb(low)
    px = []
    for y in range(120):
        for x in range(160):
            col = hi if illustrative_pixel(x, y) > (bayer[y % 4][x % 4] + .5) / 16 else lo
            px.extend((*col, 1))
    im.pixels.foreach_set(px)
    im.pack()
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes; nodes.clear()
    o = nodes.new('ShaderNodeOutputMaterial')
    e = nodes.new('ShaderNodeEmission'); e.inputs['Strength'].default_value = .85
    t = nodes.new('ShaderNodeTexImage'); t.image = im; t.interpolation = 'Closest'
    m.node_tree.links.new(t.outputs['Color'], e.inputs['Color'])
    m.node_tree.links.new(e.outputs[0], o.inputs[0])
    return m


screen_green = screenmat('Phosphor | two colour simulation on TFT', '#c1d49a', '#172821')
screen_bone = screenmat('Paper | two colour simulation on TFT', '#d9dac2', '#152528')
screen_amber = screenmat('Amber | two colour simulation on TFT', '#f1ba70', '#2b2018')


def collection(name, scene):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


def move_to(obj, coll):
    for c in tuple(obj.users_collection): c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def box(name, dim, loc, material, coll, bevel=.4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(v * MM for v in loc))
    o = bpy.context.object; o.name = name
    o.dimensions = tuple(v * MM for v in dim)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new('Machined edge / manufacturing ease', 'BEVEL')
        b.width = bevel * MM; b.segments = 3
        b.profile = .5
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    o.data.materials.append(material)
    return move_to(o, coll)


def cylinder(name, radius, depth, loc, material, coll, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius * MM,
                                     depth=depth * MM, location=tuple(v * MM for v in loc))
    o = bpy.context.object; o.name = name
    if axis == 'Y': o.rotation_euler[0] = math.pi / 2
    if axis == 'X': o.rotation_euler[1] = math.pi / 2
    o.data.materials.append(material)
    be = o.modifiers.new('Rim chamfer', 'BEVEL'); be.width = .18 * MM; be.segments = 2
    o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for f in o.data.polygons: f.use_smooth = True
    return move_to(o, coll)


def text(name, value, loc, size, material, coll):
    c = bpy.data.curves.new(name, 'FONT'); c.body = value; c.size = size * MM
    c.align_x = 'CENTER'; c.space_character = 1.2
    o = bpy.data.objects.new(name, c); coll.objects.link(o)
    o.location = tuple(v * MM for v in loc)
    o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(material)
    return o


def display(coll, x, y, z, sm=screen_green, w=57.6, h=43.2):
    # The real 2.8 inch display is 57.60 x 43.20 mm in landscape orientation.
    box('Screen surround | no touch UI', (w + 4, 1.1, h + 4), (x, y, z), glass, coll, .25)
    # A plane normal toward the viewer (-Y), with UVs oriented upright.
    mesh = bpy.data.meshes.new('LCD active area mesh')
    verts = [(x - w/2, y-.61, z-h/2), (x+w/2, y-.61, z-h/2),
             (x+w/2, y-.61, z+h/2), (x-w/2, y-.61, z+h/2)]
    mesh.from_pydata([tuple(v * MM for v in p) for p in verts], [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name='Pixel UV')
    for l, uv in zip(mesh.uv_layers.active.data, [(0,0),(1,0),(1,1),(0,1)]): l.uv = uv
    o = bpy.data.objects.new(f'LCD | {w:.2f} x {h:.2f} mm active', mesh); coll.objects.link(o)
    o.data.materials.append(sm)
    o['physical_panel_resolution'] = '320 x 240, rotated landscape'
    o['illustrative_logical_video'] = '160 x 120, 1-bit, nearest neighbour x2'
    return o


def grille(coll, cx, y, cz, width, height, style='slots', material=ink):
    # Open strips in an applied grille cassette, with a black cavity behind.
    box('Speaker grille acoustic shadow', (width, .7, height), (cx, y+.1, cz), dark, coll, .1)
    if style == 'slots':
        count = max(3, int(height / 2.8))
        for i in range(count+1):
            zz = cz-height/2 + i*height/count
            box('Grille rib', (width, .8, .95), (cx, y-.25, zz), material, coll, .12)
    elif style == 'vertical':
        count = int(width / 2.6)
        for i in range(count+1):
            xx = cx-width/2 + i*width/count
            box('Vertical grille rib', (.95, .8, height), (xx, y-.25, cz), material, coll, .12)
    else:
        # Woven cassette, modelled threads instead of a flat texture.
        for i in range(int(width/1.25)+1):
            xx = cx-width/2+i*1.25
            box('Fabric warp', (.38, .5, height), (xx, y-.4, cz), material, coll, .05)
        for i in range(int(height/1.25)+1):
            zz = cz-height/2+i*1.25
            box('Fabric weft', (width, .4, .35), (cx, y-.45, zz), material, coll, .05)


def button(coll, x, y, z, material=orange):
    cylinder('Button seat | single user control', 6.6, .7, (x, y, z-.15), dark, coll)
    o = cylinder('MUTE / UNMUTE | one tactile button', 5.4, 1.4, (x, y, z+.3), material, coll)
    o['interaction'] = 'Toggle sound; video continues. No other exposed controls.'
    return o


def feet(coll, w, d, z=1):
    for x in [-w/2+9, w/2-9]:
        for y in [-d/2+9, d/2-9]:
            cylinder('Silicone foot', 3.3, 2, (x, y, z), dark, coll)


def cable(coll, d, x=0, z=6):
    box('Recessed USB-C inlet | rear', (10, 1.2, 4), (x, d/2+.1, z), dark, coll, .1)
    points = [(x,d/2+1,z),(x,d/2+9,z),(x+8,d/2+23,3),(x+28,d/2+34,2),
              (x+63,d/2+48,2),(x+91,d/2+61,2)]
    c = bpy.data.curves.new('Low voltage cable', 'CURVE'); c.dimensions='3D'
    c.bevel_depth = .75 * MM; c.bevel_resolution = 3
    s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):
        p.co=tuple(v*MM for v in co); p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new('Thin USB cable | 5 V DC',c); coll.objects.link(o);c.materials.append(dark)


def shell(coll, w,d,h,material, base=2):
    body=box('Enclosure envelope | visual study, not printable', (w,d,h-base),
             (0,0,(h+base)/2), material, coll, .6)
    body['external_dimensions_mm'] = f'{w} W x {d} D x {h} H'
    body['manufacturing_status'] = 'Envelope study; wall thickness, bosses and closures not engineered'
    feet(coll,w,d)
    # A rear access seam, represented as a narrow rim in the study.
    box('Rear service seam', (w-.8,.4,h-base-.8), (0,d/2+.02,(h+base)/2), dark, coll, .1)
    box('Rear access cover', (w-2,.6,h-base-2), (0,d/2+.2,(h+base)/2), material, coll, .3)
    return body


def aim(o, target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()


def studio(scene, height, width=100, depth=60, camera='front'):
    env=collection('Studio / lights / camera',scene)
    box('Seamless gallery floor',(2000,2000,2),(0,0,-1),floor,env,0)
    def area(name,loc,power,size):
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        o=bpy.data.objects.new(name,data);env.objects.link(o);o.location=loc;aim(o,(0,0,height*.0005))
    # Real-world small product scale: powers of a few watts are sufficient.
    area('Large key softbox',(-.22,-.28,.34),1.8,.24)
    area('Right edge softbox',(.24,.035,.22),1.3,.18)
    area('Front fill',(-.01,-.24,.12),.3,.2)
    world=bpy.data.worlds.new(scene.name+' world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.56,.58,.6,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
    scene.world=world
    data=bpy.data.cameras.new('Product camera');cam=bpy.data.objects.new('Product camera',data)
    env.objects.link(cam)
    if camera=='rear':cam.location=(.19,.26,.18)
    else:cam.location=(.18,-.29,.19)
    aim(cam,(0,0,height*.00048))
    data.type='ORTHO'; data.ortho_scale=max(width*.00185,height*.0019,.18)
    data.lens=60
    scene.camera=cam
    scene.render.engine='CYCLES';scene.cycles.samples=args.samples
    scene.cycles.use_denoising=True
    scene.render.resolution_x=args.resolution
    scene.render.resolution_y=round(args.resolution*.88)
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'
    return env


def new_scene(name,w,d,h):
    sc=bpy.data.scenes.new(name);bpy.context.window.scene=sc
    coll=collection('Object | '+name,sc)
    studio(sc,h,w,d)
    return sc,coll


scenes=[]

sc,c=new_scene('01_Monolith',90,58,104)
shell(c,90,58,104,black)
display(c,0,-29.3,69,screen_green)
grille(c,0,-29.8,23,57,12,'slots',black)
button(c,28,-12,104,orange)
text('Song number mark','SONG A DAY',(-23,-29.85,6.5),2.0,label,c)
# Keep imprint centred under the grille rather than a large product UI.
for o in c.objects:
    if o.name=='Song number mark':o.location.x=0
cable(c,58,-27)
scenes.append(sc)

sc,c=new_scene('02_Cube',88,88,88)
shell(c,88,88,88,ink)
display(c,0,-44.3,56,screen_bone)
grille(c,0,-44.8,17,58,8,'vertical',ink)
button(c,27,-18,88,silver)
cable(c,88,-25)
scenes.append(sc)

sc,c=new_scene('03_Horizon',128,52,80)
shell(c,128,52,80,ivory)
display(c,-26,-26.3,44,screen_amber,w=48.96,h=36.72)
grille(c,39,-26.8,42,32,43,'vertical',ivory)
button(c,40,-10,80,orange)
text('Song mark','SONG A DAY',(-25,-26.85,11),2.2,dark,c)
cable(c,52,-47)
scenes.append(sc)

sc,c=new_scene('04_Timber',110,64,92)
shell(c,110,64,92,wood)
box('Inset black front baffle',(96,1.5,80),(0,-32.3,47),black,c,.25)
display(c,0,-33.3,61,screen_bone)
grille(c,0,-33.8,21,63,15,'cloth',bronze)
button(c,34,-10,92,bronze)
cable(c,64,-35)
scenes.append(sc)

sc,c=new_scene('05_Solar_Wedge',128,85,96)
# A wedged roof gives the actual 113 x 66 panel a defined light-facing surface.
w,d,h=128,85,96
verts=[(-w/2,-d/2,2),(w/2,-d/2,2),(w/2,d/2,2),(-w/2,d/2,2),
       (-w/2,-d/2,77),(w/2,-d/2,77),(w/2,d/2,96),(-w/2,d/2,96)]
me=bpy.data.meshes.new('Sloped roof envelope')
me.from_pydata([tuple(x*MM for x in v) for v in verts],[],
              [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
o=bpy.data.objects.new('Solar wedge envelope | not printable',me);c.objects.link(o);me.materials.append(ink)
b=o.modifiers.new('Small edge ease','BEVEL');b.width=.6*MM;b.segments=3
o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
feet(c,w,d)
display(c,-19,-42.8,44,screen_green)
grille(c,43,-43.1,41,22,37,'slots',ink)
# P124 is mounted landscape: 113 wide x 66 along the slope.
theta=math.atan(19/85)
roofz=86.5
panel=box('Voltaic P124 panel envelope | 113 x 66 mm',(113,66,2.6),(0,0,roofz+1.3),dark,c,.3)
panel.rotation_euler.x=theta
cell=box('Panel active face',(105,59,.25),(0,0,roofz+2.9),solar,c,.1)
cell.rotation_euler.x=theta
for i in range(1,7):
    xx=-52.5+i*15
    bar=box('Solar cell division',(.25,59,.15),(xx,0,roofz+3.1),solarline,c,0)
    bar.rotation_euler.x=theta
for yy in [-20,0,20]:
    zz=roofz+3.2+yy*math.sin(theta)
    bar=box('Solar bus bar',(105,.12,.12),(0,yy*math.cos(theta),zz),solarline,c,0)
    bar.rotation_euler.x=theta
# Put the only control on the right side, away from the panel.
cylinder('Mute seat',6.5,.8,(64.2,-20,62),dark,c,'X')
cylinder('MUTE / UNMUTE | one tactile button',5.4,1.3,(64.8,-20,62),orange,c,'X')
cable(c,85,-44)
scenes.append(sc)

sc,c=new_scene('06_Plinth',96,62,98)
# The powered base is a presentation stand, with conductive contacts underneath.
box('Powered plinth | wired, battery-free',(96,62,8),(0,0,5),black,c,.5)
box('Contact shadow gap',(83,49,1),(0,0,9.6),dark,c,.1)
box('Object on plinth',(88,55,88),(0,0,54),terra,c,.6)
display(c,0,-27.8,66,screen_bone,w=48.96,h=36.72)
grille(c,0,-28.2,27,57,11,'slots',terra)
button(c,27,-10,98,bronze)
feet(c,96,62)
cable(c,62,-31,5)
scenes.append(sc)


# An envelope layout of the recommended prototype, visibly separated along depth.
sc,c=new_scene('07_Exploded_Envelope',160,190,115)
box('Rear shell study',(90,2.5,100),(0,66,53),black,c,.6)
box('Electronics / LCD module | 73.06 x 50.54 x 10',(73.06,10,50.54),(0,18,72),pcb,c,.3)
box('Module component height allowance',(55,4,35),(0,24.5,72),chip,c,.2)
box('LCD black border',(73.06,2,50.54),(0,11,72),glass,c,.2)
display(c,0,9.7,72,screen_green)
box('Front baffle | openings not yet engineered',(90,2.5,100),(0,-22,53),black,c,.6)
display(c,0,-23.7,72,screen_green)
grille(c,0,-24.0,24,57,13,'slots',black)
cylinder('PUI 40mm x 5mm speaker envelope',20,5,(0,9,24),dark,c,'Y')
cylinder('Speaker cone',16.5,1,(0,5.8,24),ink,c,'Y')
cylinder('Speaker dustcap',6.5,2,(0,5.0,24),dark,c,'Y')
button(c,28,-9,104,orange)
box('Optional steel ballast | approx 83 grams',(68,31,5),(0,41,7),silver,c,.2)
sc.camera.data.ortho_scale=.26
sc.camera.location=(.22,-.34,.21);aim(sc.camera,(0,.018,.052))
scenes.append(sc)

# Provide a shelf context showing the monolith beside a book and a small sculpture.
sc=bpy.data.scenes.new('08_Shelf_Context');bpy.context.window.scene=sc
c=collection('Shelf context',sc)
for obj in scenes[0].collection.children[0].objects:
    if obj.type=='FONT' or 'cable' not in obj.name.lower():
        c.objects.link(obj)
studio(sc,110,260,120)
box('Shelf edge',(510,220,18),(0,50,-10),wood,c,.6)
bookmat=mat('Book cloth | warm neutral','#a69e8b',.85)
paper=mat('Book edges','#ded5be',.85)
for i,th in enumerate([15,18,12]):
    x=-100-i*th
    box('Book cloth binding',(th,112,154),(x,30,77),bookmat,c,.3)
    box('Book page block',(th-2,108,148),(x,28,77),paper,c,.1)
cylinder('Vase base',22,51,(126,26,25.5),terra,c)
cylinder('Vase neck',10,28,(126,26,64),terra,c)
sc.camera.location=(.27,-.42,.20);aim(sc.camera,(.005,.016,.062));sc.camera.data.ortho_scale=.38
sc.render.resolution_y=round(args.resolution*.64)
scenes.append(sc)

if 'Scene' in bpy.data.scenes and len(bpy.data.scenes)>1:
    bpy.data.scenes.remove(bpy.data.scenes['Scene'])

# Prefer Metal when available. Keep a CPU fallback for other machines.
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='METAL';prefs.get_devices()
    has_gpu=False
    for dev in prefs.devices:
        dev.use = dev.type != 'CPU'
        has_gpu = has_gpu or dev.type != 'CPU'
    if has_gpu:
        for sc in scenes:sc.cycles.device='GPU'
except Exception as exc:
    print('Using CPU renderer:',exc)

bpy.context.window.scene=scenes[0]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'song-a-day-concepts.blend'))
print('Saved editable Blender studies',flush=True)

if not args.no_render:
    for sc in scenes:
        if args.only and args.only not in sc.name:continue
        bpy.context.window.scene=sc
        sc.render.filepath=str(OUT/(sc.name.lower()+'.png'))
        print('Rendering',sc.name,flush=True)
        bpy.ops.render.render(write_still=True,scene=sc.name)
print('Complete',flush=True)
