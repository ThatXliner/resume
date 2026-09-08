# Camera loadout modeling references

The meshes are authored in `build_models.py`. Product photographs were consulted for form and control placement; they are not used as textures or distributed with the site.

- EOS R7 front and rear: https://melaniec.co.za/2022/07/01/the-canon-eos-r7-and-the-canon-eos-r10/
- EOS 40D multi-angle reference: https://www.thegioimayanhso.vn/canon-40d-body
- EOS 40D top photograph: https://giangduydat.vn/canon-eos-40d
- EOS 40D manufacturer brochure: https://downloads.canon.com/cpr/software/camera/40D_BC_0113W833.pdf
- C200 side panel: https://www.canosa.com.hr/canon-eos-c200-ef-24-105mm-f4l-is-ii-usm-kit-cinema-camera-profesionalna-vide/47768/product/
- EF 28–135mm: https://www.canon.com.br/produtos/produtos-para-voce/cameras/lentes-eos/zoom-normal/ef-28-135mm-f/35-56-is-usm
- EOS R7 straight rear product photograph: https://cameraclix.com.au/products/canon-eos-r7-body-mirrorless-camera
- EOS R7 top product photograph: https://excellentphoto.ca/products/canon-eos-r7-mirrorless-camera
- EF 28–135mm switch close-up: https://www.pointsinfocus.com/reviews/lenses/normal/canon-ef-28-135mm-f3-5-5-6-is-usm/

## Visual acceptance review

The current custom models are still a work in progress, not accepted as photorealistic.
Custom modeling is continuing from online product photographs. Acquiring an
external model is an option, not a prerequisite for correcting these meshes.
The September 6 review identified a floating planar lens switch panel, inaccurate rear
controls, reversed zoom/focus ring placement, unsupported barrel joints, and a solid
viewfinder block. These have been revised; the body contours, lens-specific molding,
surface finish, and optical appearance still require reference comparisons.

Retain raw exports in `output/gear-modeling/uncompressed/` before compression. Generate
the same front, rear, and side views for each R7 revision with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python-exit-code 1 --python scripts/gear/render_studio.py -- --audit
```

Inspect `output/gear-modeling/audit-{front,rear,side}.png`, then inspect the actual
browser viewer. Offline Cycles renders do not establish WebGL quality or prove that
the other bodies and lenses meet the target.

Add `--body-only` to render isolated R7 front, rear, side, and top views into
`audit-r7-body-*.png`. The September 7 R7 revision moves the mode dial to the grip
shoulder, increases grip depth, corrects the command wheel axis and width, adds
the top controls, and fuses the grip into the main shell before mesh reduction.

Use `--body-only --body=40d` for equivalent isolated 40D views. Its September 7
revision removes the screen hinge, reduces the fixed LCD width, moves the rear
controller, adds the five-button bottom row and power lever, and replaces the
generic rear disk with a recessed wheel with radial grip ridges. The top LCD and
command wheel, pop-up flash cover, and reflex mirror chamber have also been revised.
The mode dial's scene pictograms remain simplified, and full photorealism has not
been established by these corrections.

### Asset sourcing, September 6

- R7 by Salome: public Sketchfab API reports `isDownloadable: false` and no license.
  Do not extract viewer geometry. https://api.sketchfab.com/v3/models/e85512672b174fdeb521f32dd0ee7d94
- R7 by 3d_molier / 3dmi: a commercial candidate, listed at $79 on CGTrader.
  No purchase has been authorized or made; downloadable geometry has not been inspected.
  https://www.cgtrader.com/3d-models/electronics/video/canon-eos-r7-camera
- CGTrader's license guidance restricts independent retrieval and redistribution of
  purchased model files. An openly served GLB in this public repository needs a
  suitable license arrangement; do not assume the standard purchase covers it.
  https://help.cgtrader.com/hc/en-us/articles/360015124437-Royalty-Free-License
- The 40D listings found on CadNav and Open3DModel state non-commercial and personal/
  education licenses respectively. Neither has been approved as a source asset.
  https://www.cadnav.com/3d-models/model-46748.html
  https://open3dmodel.com/3d-models/3d-model-canon-eos-40d-camera_44899.html

The custom 28–135 grip is now based on the broad rounded lands in the close-up,
and the optical elements use shallow closed curved surfaces instead of flattened
spheres. This is a visual approximation, not Canon's optical prescription.
The 28–135 and 50mm II diaphragm counts follow the manufacturer's six- and five-blade
specifications: https://global.canon/en/c-museum/product/ef342.html and
https://global.canon/en/c-museum/product/ef295.html.

## Included lighting asset

`public/models/gear/studio.hdr` is Studio Small 09 by Sergej Majboroda / Poly Haven, CC0.
https://polyhaven.com/a/studio_small_09
https://polyhaven.com/license

## Rebuild

Run Blender from the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python scripts/gear/build_models.py
```

Optional asset IDs after `--` rebuild only those meshes. Editable `.blend` files are saved under `output/gear-modeling/`. Models use the viewer's Y-up coordinates and are exported without Blender's axis conversion.

Compress the exported GLBs with glTF Transform, retaining geometry and material names:

```sh
bunx @gltf-transform/cli optimize input.glb output.glb --compress meshopt --simplify false --palette false --texture-compress webp
```

The web viewer loads the compressed GLBs with Three.js and MeshoptDecoder.

## Wordmark

`canon-wordmark.svg` is the Canon wordmark, sourced from Wikimedia Commons (PD-textlogo; trademark). The normalized contour file is derived from that SVG for accurate markings on the models.
https://commons.wikimedia.org/wiki/File:Canon_wordmark.svg

### C200 rear-panel revision

Reference: https://www.cined.com/canon-eos-c200-internal-4k-raw-affordable-price/
Product photograph: https://www.cined.com/content/uploads/2017/05/Canon-C200_5-1536x864.jpg

The rear assembly now separates the lower BP-A30 battery bay, dual SD doors,
audio-channel controls, navigation buttons, and right-hand connector covers.
The operator side and handgrip placements were corrected, and the monitor faces
the operator. Connector internals remain covered; the grip and casting contours
still require closer reference matching. Four-sided C200 Blender audits are
available through `render_studio.py -- --audit --body-only --body=c200`.

C200 grip reference: https://www.adorama.com/us1739913.html
Photo: https://www.adorama.com/images/Large/1739913.jpg
The GR-V1 replaces the earlier oval with a contoured shell, rubber overmold,
rosette, padded strap, buckle, record button and control dial. The right side
also has intake louvers and audio selector covers. The C200 audit now includes
a dedicated grip-side view; these details do not establish overall photorealism.

### C200 physical scale

Canon body-only dimensions: 144 × 153 × 179 mm.
https://sg.canon/en/consumer/eos-c200/main/specification

The shared lens scale is 55 mm per unit (28–135 length 1.76 units = 96.8 mm).
The C200 bare body measured approximately 122.79 × 123.81 × 152.49 mm before
calibration. The builder calibrates the bare body to Canon's dimensions, excluding
the detachable grip and monitor from the measured bounds and preserving the EF
mount geometry and front mating plane. Live front/rear captures after this change
are in output/gear-modeling/c200-live-scale.png and c200-live-rear.png.
The WebGL checks confirm assembly and rotation, not photorealistic completion.

### 28–135 front optical group

Front photo: https://file.hstatic.net/200000782117/file/1s5a0178_614dd3ef2fb448ab9c102cf1353b0b08.jpg
Source: https://thanhmaistore.vn/products/ong-kinh-canon-ef-28-135mm-f-3-5-5-6-is-usm
The model now has the broad stepped baffle and smaller recessed inner group seen
in this photograph, plus larger front nameplate text. The website's optical
material uses thin transmission and an inner reflection layer; it is a real-time
approximation, not a recovered optical prescription. Live comparisons still
show insufficiently convincing glass reflections, so optical fidelity remains open.

### R7 mount chamber

Sensor dimensions: https://cam.start.canon/en/C005/manual/html/UG-10_Reference_0100.html
RF flange distance: https://www.canon.com.au/get-inspired/rf-lens-benefits

The R7 shell is bored after grip remeshing, with a 22.3 × 14.8 mm sensor placed
20 mm behind the flange at the shared 55 mm/unit scale. Its twelve contacts are
spread along the bottom arc and exposed above the bayonet face. The Canon mark
was raised to clear the alignment pip, and the model badge given its raised pad.
These fix front details; overall shell contour matching remains unfinished.

### R7 silhouette revision

The R7 housing height is reduced by 13%, and the model-badge shoulder is narrowed
past x=0.45. The same deformation applies to attached controls, excluding the
mount and the lens-release projection; the circular sensor chamber is cut after
deformation. Front/rear body renders were inspected for collisions. Canon front
lettering is smaller to fit the shorter viewfinder crest. This is a visual
proportion correction against the existing R7 photo, not a dimensionally complete
reverse-engineered housing.

### R7 ambient occlusion

The R7 exports a 2048px geometry-baked ambient occlusion map using a separate
BakedAO UV set. It captures local occlusion within 0.16 scene units rather than
baking directional lighting. The glTF occlusion texture and UV coordinates were
checked after meshopt compression, and the actual viewer's rear controls and
eyecup were inspected. This process now applies to R7, 40D, and C200; compressed textures and live assembled views were checked for all three. Surface grain
continues to use the original UV set. Overall photorealism remains unproven.

### EF 70–200mm f/4L IS controls

Reference: https://commons.wikimedia.org/wiki/File:Canon_EF_70-200mm_F4L_IS_USM_lens.jpg
Photo: https://upload.wikimedia.org/wikipedia/commons/2/2f/Canon_EF_70-200mm_F4L_IS_USM_lens.jpg
The f/4 model now uses the four-switch white control band between the rubber
rings: 1.2m/3m focus limiter, AF/MF, IS on/off, and IS modes 1/2. Rubber-ring widths
were corrected and the optional tripod collar moved onto the rear barrel, clear
of the zoom grip. Side placement was checked in the actual viewer. The f/2.8
example still needs its own reference-specific panel correction.

### EF 70–200mm f/2.8 example controls

Canon reference: https://www.canon.com.hk/en/product/catalog/productItemDetails.do?prrfnbr=321
Photo: https://www.canon.com.hk/public/product/3/pr_large_321.jpg
Control close-up: https://bbsimg01.kakaku.k-img.com/images/smartphone/icv/152818_f.jpg
The example uses the original IS layout: a white central four-switch panel,
1.4m/2.5m focus limiter and IS modes 1/2. Its collar is clear of the rear zoom
ring, with Canon/Ultrasonic marks near the front. Both telephoto focal-length
scales are now behind their zoom rings. The assembled C200 side view was checked
in the actual viewer. This supersedes the earlier note about a pending f/2.8
panel correction; optics and overall photorealistic fidelity remain unfinished.

### EF 50mm f/1.8 II geometry

Reference photo: https://mayanhvn.com/media/product/1651_canon_50mm_f18_mkii.jpg
Product page: https://mayanhvn.com/canon-ef-50mm-f18-ii.html
The 50mm now has a dedicated mesh builder: smooth fixed barrel, narrow front
focus rim, compact AF/MF recess, plastic mount, and a smaller recessed optical
group. Removed the generic zoom grip and nonexistent distance window. Its front
inscription includes the II designation. A continuous conical recess replaces
stacked beveled rings that produced visible moire in the live viewer. Glass size
and recess depth are estimates from the photo, not measured optical geometry.
Front three-quarter and side views were inspected in the interactive viewer.
These changes improve model specificity; full photorealistic fidelity is still
unfinished, particularly body contours and optical rendering.

### Tamron SP 35mm F/1.4 Di USD F045

Primary references: https://tamron.in/product/f045 and
https://www.tamron.com/global/consumer/lenses/f045/
Exterior photographs: https://tamron.in/v2/product_image/topside.jpg and
https://tamron.in/v2/product_image/sideview.jpg
A dedicated F045 builder replaces the generic zoom-shaped prime. Canon mount
length is 104.8mm and maximum diameter 80.9mm at 55mm per model unit. Focus grip
is toward the front, with smooth rear barrel, tapered shoulder, broad metal
mount accent, curved distance window, and compact AF/MF controls. Removed the
incorrect front-ring Canon-style inscription. Top, side and front three-quarter
views were inspected in the actual viewer. The first top inspection caught
window geometry sinking into the cylinder; subdivision before bending corrected
that visible defect. Optical construction remains an approximation, and the
assembled model does not yet establish photorealistic completion.

### R7 grip silhouette and camera bases

Rechecked the R7 front/back and top references listed above. The front grip is
narrower toward the mount while retaining its outside edge; the shutter moves
with the narrowed grip. The assembled viewer now shows more of the finger
recess and front focus-mode selector. Isolated front/side renders confirmed the
contour change and exposed two unrelated base defects: the battery plate floated
below the casting and the tripod socket protruded as a peg. The shared camera
base now seats the plate against the body and cuts a recessed, ringed socket.
This is an incremental correction; full reference fidelity remains unfinished.
The rebuilt R7 and 40D bases were inspected from below in the interactive viewer;
the R7 also received an isolated bottom render. The floating plate and protruding
socket defects are gone. The bottom render reveals that rear control attachment
and the front overmold edge still need closer inspection from grazing angles.

### Rear control seating and viewer lighting

Rear controls previously sat ahead of the main casting with no supporting rear
cover. Added a shaped rear cover to R7 and 40D, with an LCD opening. Rebuilt AO
and inspected compressed models from oblique rear angles; the R7 isolated bottom
render now shows the controls connected to the cover. The 40D LCD remains visible.
Viewer exposure is now 1.0, environment intensity .4, key .85, rim .65 and warm
fill .15. Compared R7 and C200 assembled views: black finishes retain darker
values without losing the principal highlights, and the white telephoto remains
legible. TypeScript and production build pass. These inspections establish the
specific fixes only; optics, C200 silhouette, and overall realism remain open.

### C200 front casting

Front reference: https://www.justcanon.in/products/canon-eos-c200
Photo: https://www.justcanon.in/cdn/shop/products/eos-c200_07.jpg?v=1659445922
Replaced the cuboid front with a shaped chassis, raised Canon crest, circular
structural mount casting, VIDEO cap, Cinema EOS badge, and lower 10/11 function
buttons. The handle/monitor attachment rises to clear the taller housing. An
isolated front render exposed vertical stretching of the circular casting under
body calibration; that casting now uses equal X/Y scale. The monitor cable also
now ends in a side connector. The sensor chamber and accessories still use
approximate geometry and remain part of the unfinished fidelity work.

### Optical rendering investigation

Inspected the exported GLB transmission/IOR/clearcoat extensions and the served
viewer material code. Stronger thin-film coating alone produced little visible
change at the default angle. Closed glass surfaces now render front faces only,
without an additional clearcoat lobe; inner reflection opacity is .06. The
28-135 front element has greater curvature, with its apex remaining behind the
rim. Rotating the actual viewer reveals a distinct reflected highlight across
that glass. The concentric internal baffles remain too dominant and the optical
result is still not photorealistic. Coating thickness and curvature are visual
approximations, not a recovered manufacturer optical prescription.

### 28–135 front recess revision

Compared directly with the previously downloaded Thanh Mai front close-up.
Replaced the eight strongly rounded internal steps with a continuous shallow
recess and six narrow grooves, using a rough black optical-barrel material.
Both default and rotated viewer captures show the oversized ring highlights
removed. Groove clearance was increased to avoid intersecting the conical
surface, but faint speckling remains visible and needs further diagnosis (the
last clearance change did not establish that artifact as solved). Glass depth
and coating reflections still need refinement. Production build passes.

### Baffle speckling diagnosis

A temporary test disabling received shadows on the optical recess did not
change the speckling; that test was reverted. Replacing the six tiny groove
meshes with a mapped roughness texture removed the speckling in matching and
second-angle viewer captures. The recess has a dedicated preserved UV set;
exported metallicRoughnessTexture presence was checked in the compressed GLB.
Fine rings remain visible as finish variation without subpixel geometry edges.
Production build passes. This resolves the observed baffle artifact, not the
remaining optical-depth or complete photorealistic-fidelity requirements.

### Refraction depth and next renderer test

Verified runtime MeshPhysicalMaterial values with a temporary diagnostic, then
removed it. Outer glass now uses finite approximate thickness (.16 units for
28-135, .12 for 35, .06 otherwise). Default/front/telephoto views were checked;
the visual change is small and does not establish realistic multi-element
refraction. A tinted inner-reflection trial was reverted because it did not
produce a meaningful improvement. TypeScript and production build passed.
Next investigation: an isolated progressive path-tracing comparison using
https://github.com/gkjohnson/three-gpu-pathtracer, whose documented renderer can
trace multiple bounces. The maintainer has announced eventual WebGL deprecation
(https://github.com/gkjohnson/three-gpu-pathtracer/issues/779); any prototype must
use a verified compatible release and preserve responsive interaction. No path
tracer dependency or production integration has been added yet.
# C200 filter housing and finish follow-up

## Grip finish

The camera grips use the CC0 normal and roughness maps documented in
`textures/README.md`, calibrated against the saved R7 front and rear photos.
The first unadjusted scan trial was rejected after browser inspection: it was
too glossy, and three repeats averaged the grain into a smooth highlight.
The final recipe uses a matte roughness range, stronger molded relief and
1.25 repeats shared by normal and roughness maps. Black body color is retained.
The C200's painted castings keep their distinct procedural crinkle finish.
World-area UV density normalization keeps the same grain size across differently
sized rubber parts. Rear inspection also caught a buried 40D thumb pad and
labels behind the rear-cover face. Both still-camera thumb pads now overlap the
cover slightly with their outer faces exposed; the 40D cover labels sit just
outside its rear surface.

## Telephoto optical depth and aperture

Canon specifies eight rounded diaphragm blades for both modeled IS telephotos:
https://global.canon/en/c-museum/product/ef391.html and
https://global.canon/en/c-museum/product/ef365.html.
The f/4 block diagram places the diaphragm near the middle of the optical train:
https://global.canon/ja/c-museum/wp-content/uploads/2015/05/ef391-lens-construction2.gif.
Replaced the shallow nine-blade approximation with eight rounded, blackened
blades deeper in the barrel. Internal elements remain a reduced visual model,
not a full optical prescription; the f/2.8 depth is approximate.

Front reflection reference for the original f/4 IS:
https://www.fredmiranda.com/forum/topic/1924402/0
Image https://www.fredmiranda.com/forum/ufiles/54/2985454.jpg.
With glass hidden in a temporary browser diagnostic, the gray bowl remained.
Reducing the lining's specular response removed it. The final flocking uses
Blender Specular IOR Level 0.05 rather than the default 0.5. A separate black
front sleeve covers exposed white housing inside the filter rim. Removed the
temporary scene diagnostic after tracing these causes.

HDU-2 handle primary reference:
https://www.usa.canon.com/shop/p/hdu-2-handle-unit
Image: https://s7d1.scene7.com/is/image/canon/2421C001_primary
The reference shows a single hollow casting, scalloped hand opening, transverse
accessory sockets, cold shoe, recessed top mounting insert and central knurled
mounting wheel. Rebuilt these features and removed the unsupported wide cage
plate from the previous model. The monitor arm moves upward with the handle
to maintain clearance. Dimensions remain photo-estimated; the casting is not
claimed to be a manufacturer CAD model.

Verification caught a filled hand opening despite a successful export. The
profile helper accepted clockwise outlines with inward normals, which made the
boolean unreliable. It now normalizes winding before building solids; an
unobstructed ray through the hand opening is required before export. Confirmed
the resulting opening in the actual viewer and inspected the side/top Blender
audit renders. The wider audit framing includes the raised monitor.

The front photo from https://www.justcanon.in/products/canon-eos-c200 shows a
clipped-corner filter cassette, four retaining screws, blue filter surround and
narrow gold border inside the mount. The generic still-camera insert has been
replaced with this assembly. The actual sensor plane is placed at EF register
depth behind the visible filter assembly. Canon lists the sensor as 26.4 × 13.8
mm at https://sg.canon/en/consumer/eos-c200/main/specification; those dimensions
set the underlying sensor plane rather than the visible filter housing.

The same photo and the saved operator-side photo show a coarse painted finish
on the circular front casting and inset control casting. Those surfaces now use
a separate crinkle-paint material, distinct from the smoother housing polymer
and softer rubber grip. This is a procedural approximation of the reference
finish, not a scanned material.

### Still-camera eyepieces

R7 rear reference: https://cameraclix.com.au/cdn/shop/products/r7_back_body_1800x1800.webp?v=1653368444
40D front/rear/side reference: https://bizweb.dktcdn.net/100/107/650/products/allroundview-jpeg.jpg?v=1573647746827
Canon R7 diopter operation: https://cam.start.canon/en/C005/manual/html/UG-01_Preparations_0100.html

The two bodies now use separate rubber cup proportions and an inner optical
carrier with a shallow curved glass face. The R7 has the rectangular eye sensor
beside its aperture; the 40D has a centered aperture and lower retaining rail,
without an eye sensor. Knurled diopter wheels sit beside the eyepieces. These
remain reference-based geometric approximations, not optical prescriptions.

The rear display pass uses the same R7/40D rear references. The 40D bezel was
partly buried in the rear cover: its rear surface was at rz−0.0275 while the
cover reached rz−0.041. The frame now sits outside that cover, with a perimeter
gasket, inset black dielectric display face, and logo on the visible lower
frame. Display glass has a separate material from distance windows and optics,
so correcting its blue-gray metallic appearance does not change lens glass.
The R7 hinge now has two barrel sections separated by its central joint.

The 40D four-view reference also shows two adjacent vertical rubber terminal
covers, with molded VIDEO OUT, sync, remote and USB markings. The previous
shared model incorrectly divided that area horizontally. The 40D now has its
own paired flaps, recessed surround and low-contrast molded symbols. A CF-card
door perimeter follows the opposite side; its points are ray-projected onto
the casting/grip surfaces and fail the build if they miss the housing.

28–135mm control pocket refinement uses the saved Points in Focus close-up:
https://static1.pointsinfocus.com/2010/08/canon-ef-28-135mm-f3-5-5-6-is-usm/EF-28-135mm-f-3.5-5.6-IS-USM-controls.jpg
The control insert now sits in a boolean-cut curved barrel pocket rather than
on the housing surface. The pocket is taller around the circumference, with
larger individual switch wells, revised spacing, a stabilizer position mark,
and a lower retaining screw. All insert components follow the barrel radius.

### Control Ring Mount Adapter EF–EOS R

User confirmed ownership of the control-ring version. Canon's product photo:
https://s7d1.scene7.com/is/image/canon/2972C002_control-ring-mount-adapter-ef-eos-r_primary-1
Manual: https://gdlp01.c-wss.com/gds/2/0300032192/01/crm-adapter-ef-eosr-im-eng.pdf
The 2025 Canon EOS R catalog specifies 74.4 × 24.0 mm for this version.
The model now uses 24/55 scene units between mating planes, a stepped painted
housing, rear silver trim and five rows of diamond control-ring knurling.
R7 mounting copy identifies the control ring. Lens bayonets (local z=0…0.088)
now insert into the receiving mount, with local z=0.088 on its mating plane;
previously the entire bayonet sat forward of it. Viewer and study renderers use
the same corrected assembly offsets.

Distance-window carriers on the 28–135mm and both 70–200mm models are now
subdivided and bent around the barrel radius, together with their glass and
printed markings. The prior tangent boxes lifted their outer edges away from
the housing. Window glass uses the black dielectric material introduced for
inactive displays; this does not change the transmissive optical elements.

The R7/40D cast housings, grip cores and rear covers now use the painted finish
rather than the smooth button/trim polymer. An initial viewer comparison showed
oversized shoulder grain because independent UV packing changed texture scale.
Painted surfaces now use the same world-area UV normalization as scanned grips;
the paint's separate sixfold repeat keeps its grain finer than the rubber.

A later rear-oblique check showed the 40D terminal assembly still stood too
far off the side. Its tessellated covers and molded markings now project onto
the actual casting surface, retaining 45% of their prior outward depth. The
lower side fasteners are also seated by ray intersection; missing intersections
fail the build instead of silently leaving detached details.

C200 rear-detail pass uses the saved CineD rear photograph:
https://www.cined.com/content/uploads/2017/05/Canon-C200_5-1536x864.jpg
Added the BP-A30 white identification strip, individual charge-indicator dots,
check membrane/legend, battery-release tab, XLR retaining screws and PUSH
markings. The connector flaps now carry drawn headphone, USB and network
symbols in place of generic text labels. Small legends are geometric lettering;
readability remains dependent on viewer zoom and rendering resolution.

LM-V1 monitor controls follow page 17 of Canon's C200 manual:
https://gdlp01.c-wss.com/gds/3/0300027483/02/eosc200-200b-im2-en.pdf
The monitor now has a left control column (FUNC, MENU, joystick, MIRROR,
CANCEL, DISP), a separate display bezel, black inactive glass, a bottom mounting
socket and VIDEO connector. Removed the invented STBY/settings/safe-frame
readout. The cable's monitor end is moved to the modeled VIDEO connector.

C200 viewfinder geometry follows the saved rear product photo and page 40 of
the same Canon manual. The taller rubber opening surrounds a rectangular curved
optical face and an eye sensor on the left when viewed from behind. Its diopter
control is a sliding lever below the EVF housing, rather than a still-camera
side wheel. This remains simplified optical geometry, not a full EVF lens stack.


40D flash hood topology follow-up: replaced the bevel-then-subdivide extrusion
with a longitudinal loft, rounded end stations, and sampled perimeter edges.
The local interactive side view no longer shows the previous horizontal bands.
Front-oblique inspection still shows a small surface blemish near the middle of
the hood; this is unresolved and requires geometry inspection. Overall body
finish and lens optics remain visibly synthetic. C200 modeling remains paused.
Browser captures: /tmp/40d-loft-dense-front.png and
/tmp/40d-loft-dense-side.png. Production build passed during this pass; final
perimeter resampling changed only the generated 40D asset and generator.


40D hood blemish resolved: ray inspection of the unjoined model found the
continuous cast housing outside the hood at y=.96/1.0, z=.24 on the left side.
The old cavity subtracted only the hood volume, leaving exterior shell islands.
Widening and raising the hidden cavity removed those islands. All 24 sampled
side rays now encounter the hood first. Browser front-oblique confirmation:
/tmp/40d-pocket-front.png. The 40D-only EF flange was also reduced from radius
.626 to .591, with its fasteners moved inward, reducing the broad exposed silver
annulus at the lens joint. Both the 28–135 and 70–200 f/4 were inspected attached;
see /tmp/40d-flange-after.png and /tmp/40d-flange-tele.png. Rear inspection:
/tmp/40d-pocket-rear.png. These repairs do not establish photorealism.


Live-view optics/environment pass: disabling scene.environmentIntensity removed
the striped glass highlight; changing only material.envMapIntensity had no effect.
The installed Three.js WebGLRenderer overrides material intensity when envMap is
null and scene.environment is used (WebGLRenderer.js, environment uniform update).
The live scene now generates a PMREM environment from four broad light cards,
with neutral fill, and assigns that map explicitly to optical glass materials.
The old HDR remains available for the separate Blender/path-tracing studies.
Outer coating range is now 110–125 nm and glass environment intensity 1.2.
28–135 inner retaining ring/aperture housing now use the matte internal finish;
its aperture blades use blackened steel. The striped highlight is gone, but the
central pale crescent/reflection is still visibly unlike the reference. Do not
claim optical fidelity from this pass. Both body defaults, the R7 rear, owned
telephoto, and available-tab rendering were inspected. Type check and production
build passed; no browser errors. C200 geometry was not changed. Captures in /tmp:
28-interior-matte.png, r7-softbox-fill-rear.png, r7-softbox-tele.png,
c200-softbox-check.png. No path tracing was integrated into the live viewer.


28–135 inner chamber correction: a diagnostic ray from (0,.1,3), direction
(0,-.22,-1), previously hit the exterior Taper shoulder through the optics at
z=.36. There was no inner wall between the front recess and aperture. A dark
continuous chamber now joins the recess at r*.405/z=l-.32 to the aperture outer
edge; the same ray now hits Zoom inner optical chamber at z=1.19885. The broad
pale crescent disappeared in the actual viewer. The six aperture blades now fill
the complete annulus with rounded inner edges instead of leaving wedge gaps.
The Ø72mm inscription span was tightened from .42 to .30 radians. Rebuilt only
28–135; white lens geometry is unchanged. Front/oblique views were checked on R7
and 40D, with no browser errors; production build passed. Captures:
/tmp/28-iris-front.png, /tmp/28-chamber-r7-angle.png,
/tmp/28-chamber-40d-angle.png. The central optical reflections are still too plain
and photorealism is not established.


28–135 front optical profile: Canon Camera Museum construction diagram:
https://global.canon/en/c-museum/product/ef342.html
https://global.canon/ja/c-museum/wp-content/uploads/2015/05/ef342-lens-construction.gif
The diagram shows an asymmetric curved front element, unlike the old symmetric
biconvex mesh. optical_element now accepts independent rear curvature, defaults
to its previous profile for other lenses, and rejects intersecting center faces.
The 28–135 front uses a negative meniscus with .075 edge thickness, front sag .10,
rear sag .135 (.040 center thickness). These are visual approximations from the
diagram, not Canon's optical prescription. The front face position is preserved;
the recess/chamber moves .035 back to clear the rear glass surface. The live
viewer was inspected; the separate tracing study reached 453 samples in 82s at
450x450. It still lacks convincing layered internal reflections. Do not ship
path tracing as a presumed solution to model fidelity. The study also now sets
material.castShadow=false for glass: its tracing library ignores the mesh flag
for that purpose. This latest optical pass is local, after snapshot b6b3261.

40D rear printed symbols: Canon EOS 40D instruction manual, page 17:
https://gdlp01.c-wss.com/gds/6/0900008236/01/EOS40D_HG_EN.pdf
Compared with the four-view product photograph (40d.jpg). Replaced the incorrect
LV text with Print/Share artwork and STYLE with the Picture Style swatches.
Playback/erase ink belongs above-right of the bottom buttons, not on their faces.
Added the blue index/reduce and enlarge symbols below the AE/AF buttons. These
new markings use planar polygons projected onto the rear cover/overmold, avoiding
raised tubes for printed strokes. Existing R7 markings are unchanged.
Verified regenerated mesh in the live viewer at rear and rear-oblique angles:
/tmp/40d-legends-final-rear.png and /tmp/40d-legends-final-oblique.png.
New blue symbols and Picture Style artwork are visible and follow the cover.
The AE asterisk remains poorly visible; the upper button group, eyepiece and
rubber/shroud transitions still need comparison and correction. This pass does
not establish photorealism and remains local. Meshopt export and diff check pass.

40D control seating and Eyecup Eb pass:
The rear button depth is now measured against the cover/overmold BVH for each
button, with an annular bezel and a separate satin plastic cap. The AE-lock mark
uses three crossing ink strokes rather than the undersized font asterisk.
Eyecup identification: Canon's EOS 40D support/catalog lists Eyecup Eb:
https://www.canon.com.hk/en/product/catalog/productItemDetails.do?prrfnbr=100075
Separate genuine accessory reference:
https://www.cameranu.nl/p2739/canon-eyecup-eb
https://static.cmra.nu/139/1399616414_679.jpg
(local eyecup-eb.jpg). This shows an open U-shaped rubber surround, two lower
feet and an exposed hard carrier/retaining rail. The 40D cup now has the lower
central opening and additional lip profile stations. R7/C200 profiles retain
their previous loops; no optical simulation claim is made from this change.
Live-view verification: /tmp/40d-eb-rear.png and /tmp/40d-eb-oblique.png show the
open lower eyecup, exposed retaining rail, visible AE asterisk and seated button
rims. The satin caps now catch separate highlights instead of reading as rubber
bumps. Remaining fidelity gaps include the opaque-looking finder optic, broad
body/overmold transitions, subdued marking contrast and the lens optics. This
is a local revision, not proof that the full photorealism goal is complete.

Live studio rear-light/material inspection:
The existing rear spotlight moves from (4,2,-3), intensity 20 to (-3,3,-5),
intensity 55; its reflection card moves to the same rear quadrant and widens.
This brings the rear controls out of shadow without adding lights/shadow maps.
Rubber normal strength in the viewer changes from exported strength * .8 to
* .35: the brighter rear view exposed excessively deep-looking grain. Paint
normal strength stays unchanged. Checked 40D rear before/after normal adjustment
(/tmp/40d-rear-balanced-light.png, /tmp/40d-rear-reduced-normal.png), R7 front,
side and rear (/tmp/r7-balanced-{front,side,rear}.png), and the white 70-200 f/4
on 40D (/tmp/40d-70-balanced-front.png). The new views improve visibility but
still show synthetic optics, simplified controls and body transitions. These
renderer changes remain local and do not prove photorealistic fidelity.

28-135 optical recess isolation and machining pass:
Temporarily hid only the outer glass material in the live viewer. The grey
corrugated recess remained (/tmp/28-no-outer-glass.png), locating that appearance
in the underlying geometry, not solely the front transmission shader. Restored
the outer material immediately after the diagnostic. Compared the existing
28-135-front.jpg: narrow annular cuts with broad lands and stepped inner group
retainers. Replaced the sinusoidal recess corrugation with ten narrow V cuts;
added four retaining shelves extending into the chamber wall. Dimensions remain
visual approximations, not a recovered optical prescription. Inspected front
and oblique views (/tmp/28-stepped-recess-{front,oblique}.png). Reduced recess
sampling from the trial 240 rows to 120; compressed GLB is 1.60 MB rather than
1.79 MB. Final capture: /tmp/28-stepped-final.png. Central coated reflections
still look like simple discs; that fidelity gap remains open. Not published.

28-135 inner dielectric/coating pass:
Replaced this lens's inner brown metal/opacity-.12 layer with a nonmetallic,
black-diffuse additive reflection layer, opacity 1, IOR 1.52, iridescence 1 and
280–300 nm thickness range. This is a raster reflection approximation, not a
multielement transmission simulation. Other lenses retain their existing
material settings pending their own checks. Three.js material/shader references:
https://threejs.org/docs/pages/MeshPhysicalMaterial.html
node_modules/three/src/renderers/shaders/ShaderChunk/iridescence_fragment.glsl.js
Initial dielectric test at the old curvature stayed disc-like and blue
(/tmp/28-inner-dielectric.png). Increased the two 28-135 inner surface sags to
.055 (visual approximation; not a recovered Canon optical prescription), while
retaining positions/radii. The curved surfaces now catch moving, distinct
softbox reflections in front and both oblique views:
/tmp/28-curved-dielectric.png, /tmp/28-curved-dielectric-oblique.png,
/tmp/28-curved-dielectric-opposite.png. The reflected coating colours are still
an approximation and the optics remain visibly synthetic. GLB stays 1.60 MB.

R7 rear screen/speaker/control pass:
Compared r7-rear.webp (CameraClix product reference). Thin glass/gasket cube
bevels were clamped by their .010 thickness, leaving nearly square corners.
The R7 now uses an explicitly rounded outline extruded to that thickness;
outline radius no longer depends on thickness. Added six real boolean speaker
perforations with dark recessed floors below the finder/dial gap. A trial .09
finder shift was rejected because it visibly misaligned the finder and hot shoe
(/tmp/r7-surround-rear.png); original finder placement is retained. Replaced the
small font AE asterisk with three strokes and added the blue playback frame,
with a smaller triangle inside it. These changes are restricted to the R7.
Final R7 viewer checks: /tmp/r7-rear-final.png and
/tmp/r7-rear-final-oblique.png. Speaker recesses remain visible with the original
finder placement; the AE and framed playback marks are visible. Oblique view
shows the thin glass outline and its corner radius. Compressed R7 is 3.57 MB.
The side door geometry, finder optics, broad shoulder transitions and overall
material response remain visibly simplified. This pass stays local and does
not establish photorealism. Earlier snapshot b6b3261's GitHub Pages workflow
34161252863 was independently confirmed completed/success during this pass.

R7 terminal covers and port-side strap eye:
Reference: https://cameraland.co.za/products/canon-eos-r7-body
https://cameraland.co.za/cdn/shop/files/cameraland-canon-eos-r7-mirrorless-camera-body-04.webp?v=1755191805&width=1400
(local r7-terminals.webp). Four covers replace the generic rectangle: sloped
MIC cover, long remote-terminal cover, lower headphone cover, and tall HDMI/USB
cover. Outlines use coordinates from the image; molded MIC/HDMI text and remote,
headphone and USB symbols follow the same surface projection as the covers.
Added a shaped leatherette surround and thin recessed-looking seam borders.
All cover vertices are projected onto the real housing before the common R7
body deformation. Added a controllable outline-rounding parameter to profile;
its existing default is preserved for all previous callers.
The former square strap fitting overlapped MIC. Replaced it with a raised oval
metal eye above the covers, posed against the shoulder normal with a stable
across-camera axis (the initial shortest-arc rotation rolled the slot). Removed
two generic side screws that incorrectly crossed the headphone/HDMI covers.
The existing positive-side fill light changes from (2,1,5), intensity 8 to
(4,3,1), intensity 25; the same three lights/shadow maps remain in use. Initial
side captures exposed these overlaps/alignment issues before final correction:
/tmp/r7-terminals-side.png and /tmp/r7-ports-final-side.png.
The close-up exposed severe panel shading artifacts. Disabling normal/AO maps
and then live shadows did not remove them; both diagnostics were fully restored.
Denser interior triangulation, zeroing custom normals and smoothing the sampled
support did not resolve the artifact. Rebuilding the deformed panel mesh data
(vertices/faces/materials, with automatic smooth normals) finally removed the
rippling. Retained custom-normal data was the decisive issue, not a material
colour adjustment. Covers retain a smooth vertical support profile sampled
across the casting depth, with narrow clearance; source outlines remain intact.
Final checks: /tmp/r7-fresh-normals-final.png (side close-up),
/tmp/r7-clean-ports-oblique.png and /tmp/r7-clean-ports-front.png. Four shaped
covers, molded symbols and the horizontal oval strap eye are visible without
the old overlaps or rippled panel shading. GLB is 3.90 MB. Broader body shading
and optics still need fidelity work; consider retained custom normals when
investigating remaining deformed-surface artifacts. All changes remain local.

### R7 shoe and casting verification

The R7 shoe now has a metal bed, inset black contact block, one large sync
contact, four smaller communication contacts and a modeled accessory-contact
row. Compared with r7-top.png and Canon's EOS R7 manual (21 accessory pins plus
five flash contacts):
https://global.canon/ja/c-museum/wp-content/uploads/2023/06/dslr901_en.pdf
Live checks: /tmp/r7-shoe-top-shortlens.png and
/tmp/r7-shoe-rear-oblique.png. Bed and contacts stay attached in both views.
Mechanical dimensions remain photo-derived approximations.

Top housing streak diagnosis: removing the roughness map initially appeared to
remove streaks, but that also changed effective roughness to 1. Holding uniform
roughness at 0.48 retained the streaks (/tmp/r7-shell-uniform-roughness.png).
Disabling the normal map alone also retained them. Matching roughness tiling to
normal tiling did not solve them. All runtime diagnostic overrides and the
unproven tiling change were reverted. The earlier whole-housing fresh-normal
experiment likewise did not improve the housing. Investigate casting geometry;
do not cite map removal as a successful fix.
A 24-iteration casting smoothing trial (baseline 4) did not remove the streaks
in /tmp/r7-casting-smoothed-oblique.png. Reverted source and published-path GLB
to the shoe revision. The ignored editable blend and uncompressed R7 output
still contain this rejected smoothing trial; regenerate them from source before
using them. Disabling live shadow maps also retained housing streaks
(/tmp/r7-casting-no-shadow.png); restored shadow settings. Geometry remains a
hypothesis, not a proven root cause. A next controlled comparison should hold
roughness at 0.48 while disabling both normal mapping and AO, rather than
changing effective roughness when removing a map.

### R7 crown deformation sampling

Controlled diagnostic /tmp/r7-controlled-no-maps.png holds roughness at 0.48
and disables normal, roughness and AO maps together. Broad bands remain.
Restored all runtime settings after the comparison. Increasing pre-remesh
smoothing alone had not helped. Subdividing long upper-housing triangles before
the nonlinear crown bend reduces broad shoulder bands in the actual viewer:
/tmp/r7-tessellated-casting.png, compared with /tmp/r7-shoe-rear-oblique.png.
The first subdivision export exposed rippled rear-cover shading, so the final
mesh must also discard pre-deformation split normals. Neither a favorable
shoulder view nor a successful export establishes completion.
Final retained implementation subdivides upper shell/rear-cover edges longer
than 0.05 model units before bending, then rebuilds those meshes with smooth
normals from their final vertex positions. The combination matters: replacing
normals alone had not removed broad shoulder bands; subdivision alone retained
bad rear-cover split normals. Verified final export in the interactive viewer:
/tmp/r7-formed-normals-oblique.png, /tmp/r7-formed-normals-rear.png and
/tmp/r7-formed-normals-front.png. Rear rippling is removed and the shoulder bands
are reduced. Remaining geometry, lettering, small seams and optics still fall
short of the reference. Final compressed R7 is 4.44 MB (previous shoe version
3.93 MB); loading remains opt-in. Editable blend and uncompressed GLB have been
regenerated from the retained source, superseding the stale-output note above.

### R7 mode dial reference

Canon's Part Names page provides the twelve-position mode dial diagram:
https://cam.start.canon/en/C005/manual/html/UG-00_Before_0090.html
https://cam.start.canon/en/C005/manual/html/screens/UG-00_i0210.png
Local reference: output/gear-reference/r7-mode-dial.png.
The prior ten-position generic dial omitted Fv and Creative Filters and placed
SCN/custom positions in the wrong sequence. The R7-specific dial now includes
all twelve, larger type, outlined custom/Auto marks, an overlapping-circle
Creative Filters symbol and a white body index seated on the shoulder.
The first outlined C1/C2/C3 treatment crowded adjacent labels. Replaced it with
stacked dark C/numeral glyphs on white badges, matching the product photo; Auto
uses a green framed A with a raised plus. The dial is set to Tv at the index,
as in r7-top.png. Final live checks: /tmp/r7-dial-final-top.png and
/tmp/r7-dial-final-oblique.png. Twelve positions and their symbols are now
visible in the interactive viewer. Fine glyphs still depend on zoom/resolution;
this is not a claim that the full camera is photorealistic. R7-only geometry
change; both regenerated GLB and editable source are local and uncommitted.

### R7 shutter-area controls

Compared top controls with output/gear-reference/r7-top.png at original
resolution. The main wheel has a diamond pattern, while the prior generic dial
used long axial ribs. Replaced it with a cylindrical core and a single mesh of
12 axial rows × 32 diamond positions, using the existing satin control plastic.
The first viewer check exposed over-large teeth and too much wheel above the
casting. Reduced tooth relief from .008 to .003 model units and lowered its
center by .023. Enlarged the M-Fn/ISO/LOCK legends; added the power selector's
white index and movie pictogram. Printed marks follow the casting surface.
