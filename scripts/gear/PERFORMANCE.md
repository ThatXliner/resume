# Visitor loading behavior

The equipment section starts with lazy-loaded PNG previews. Three.js, WebGL,
compressed meshes, and model textures are not loaded until a visitor presses
“Explore in 3D” or selects equipment. The selectors and specs use a small module
that does not import Three.js at runtime until that interaction.

Only the selected body/lens and, for R7, its adapter are requested. Model promises
are deduplicated; successfully loaded models are reused. Selection versioning
prevents an older request from replacing a newer choice. Failed loads can be
retried without discarding the current scene. Initial failure keeps the static
preview and specs available.

Meshopt uses one worker for mesh decoding. Rendering caps pixel ratio at 1.5 on
fine pointers and 1.25 on coarse pointers, uses cached 1024px shadow maps, renders
only dirty frames, and pauses its update loop offscreen or in a hidden tab.
Resources are disposed on navigation. Path tracing is not part of the site UI.

Verified against the production preview on 2026-09-07:
- Before interaction: zero GLB requests and no WebGL canvas.
- Starting the default setup: only r7.glb, 28-135.glb, adapter.glb (5.56 MB total).
- Switching to 40D requests just 40d.glb; returning reuses loaded assets.
- Rapid available/owned/body changes leave the last selected setup displayed.
- Aborted initial model request preserves the preview and offers retry.
- Aborted later lens request preserves the scene; selecting it again retries.
- Successful recovery verified for both failure cases.
- 390×844 mobile layout inspected; type check and production build passed.

These checks establish loading behavior, not a general frame-rate guarantee on
all devices or photorealistic model quality. Browser captures remain local in
/tmp/gear-production-preview.png and /tmp/gear-production-mobile.png.
