# Camera rendering study

Run the existing Astro dev server and open:
http://127.0.0.1:4321/@fs/Users/me/Developer/mine/thatxliner.github.io/output/gear-modeling/render-study.html

The local HTML loads `scripts/gear/render_study.ts`. It is outside the published
site. The main loadout still uses its existing renderer.

Confirmed remaining lighting limitation: Three.js RectAreaLight has no shadow
support (https://threejs.org/docs/pages/RectAreaLight.html). The installed
`aomap_fragment.glsl.js` attenuates indirect diffuse/specular contributions, not
the rectangular lights' direct contributions. This explains why deeply recessed
eyecup surfaces can retain bright highlights despite baked AO. Further lighting
work should compare shadowed illumination with environment-based studio
reflections, rather than compensating solely with darker material colors.

The main viewer now uses three shadow-casting spotlights with HDR reflections.
The R7 rear comparison removed the bright unshadowed strip inside the eyecup;
the C200 handle and lens mount also receive directional occlusion. Shadow maps
update during equipment changes and lens movement, then remain cached while
only the viewing camera orbits. The separate path-tracing study still uses its
area-light experiment. This improves recess shading but is not a claim that the
models or their rendering are yet photorealistic.

Pinned three-gpu-pathtracer 0.0.24 accepts Three >=0.180.0; the project uses
0.185.1. Documentation: https://github.com/gkjohnson/three-gpu-pathtracer
The WebGL renderer has announced eventual deprecation in issue 779, so this is
an evaluation, not an established production dependency choice.

Both canvases use the same R7, adapter, 28-135, lighting, camera and materials.
Raster shadows use the study's comparison rig. The tracing side uses 16 bounces,
450x450 tracing resolution displayed at 600x600, and a small denoising kernel.
There are front/three-quarter presets and a pause control; accumulation stops
at 512 samples. The study exposes `window.renderStudy` for local diagnostics.

Initial malformed tracing was caused by normalized integer GLTF attributes.
Converting normalized attributes to float before building the tracing scene
fixed the geometry. Tone-mapping changes alone did not fix that failure.
The final study uses AgX on both canvases.

Observed around 134 samples in 27 seconds with matching raster shadows on this
machine. Glass reflections differ and ray-traced contact shadows are present,
but visible noise and soft lettering remain. A prior 168-sample denoised image
also remained noisy. These are evidence of a working study, not photorealistic
completion or acceptable interactive performance. Study TypeScript and the
production build pass. Further work must measure front/rear behavior, convergence,
and switching latency before considering an idle-only integration.

The directional-light baseline reached 512 samples in about 91 seconds. A second
study with three rectangular softboxes produced recognizable studio reflections,
but the accumulated result still softened markings and retained noise. The main
viewer therefore retains raster rendering. Its initial rectangular-softbox
trial was replaced by the shadow-casting rig described above. The study remains
a separate lighting experiment, not an exact copy of the current viewer rig.

Rubber normal-map repetition was reduced from five to three, with normal strength
scaled by 0.8 instead of 0.6. A 1.5-repeat trial made the grain visibly oversized
and was rejected. The C200's separate crinkle-paint material uses six repeats and
0.6 strength scaling: using the rubber settings made its grain oversized in the
actual viewer. Fine polymer and magnesium grain retain the prior settings.
