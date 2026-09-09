import quilliumScreen from "../assets/products/quillium-revision.png?url";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

/** One native scroll position drives the stage. No scroll interception or animation dependency. */
export async function initResumeFilm() {
  const root = document.querySelector<HTMLElement>(".film");
  if (!root) return;
  const canvas = root.querySelector<HTMLCanvasElement>("canvas")!;
  const status = root.querySelector<HTMLElement>(".film-status")!;
  const toggle = root.querySelector<HTMLButtonElement>(".motion-toggle")!;
  const chapters = [...root.querySelectorAll<HTMLElement>("[data-scene]")];
  const panels = chapters.map((chapter) =>
    chapter.querySelector<HTMLElement>(".chapter-frame")!,
  );
  const galleryHeading = root.querySelector<HTMLElement>(".gallery-heading")!;
  const galleryFoot = root.querySelector<HTMLElement>(".gallery-foot")!;
  const prints = [...root.querySelectorAll<HTMLElement>(".film-gallery a")];
  const indexSection = root.querySelector<HTMLElement>("#music")!;
  const cameraSection = root.querySelector<HTMLElement>("#observe")!;
  const sourceSection = root.querySelector<HTMLElement>("#open-source")!;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  let staticMode = reduced.matches;
  const galleryControl = document.createElement("div");
  galleryControl.className = "gallery-explore";
  galleryControl.hidden = true;
  galleryControl.tabIndex = 0;
  galleryControl.setAttribute("role", "region");
  galleryControl.setAttribute(
    "aria-label",
    "Photo gallery. Drag to look around or swipe sideways or use left and right arrow keys to explore. Scroll down to continue.",
  );
  galleryControl.innerHTML =
    '<div class="gallery-explore-hint"><button type="button" aria-label="Look left">←</button><span>Drag to look around · Scroll down to continue</span><button type="button" aria-label="Look right">→</button></div>';
  root.append(galleryControl);
  let galleryPitch = 0;
  let galleryPitchTarget = 0;
  let galleryYaw = 0;
  let galleryYawTarget = 0;
  const turnGallery = (amount: number) => {
    galleryYawTarget += amount;
    schedule();
  };
  galleryControl.addEventListener(
    "wheel",
    (event) => {
      const horizontal = event.shiftKey ? event.deltaY : event.deltaX;
      if (
        !event.ctrlKey &&
        (event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY))
      ) {
        event.preventDefault();
        turnGallery(horizontal * (event.deltaMode === 1 ? 16 : 1) * 0.0025);
      }
    },
    { passive: false },
  );
  let drag: { id: number; x: number; y: number } | undefined;
  galleryControl.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || (event.target as Element).closest("button"))
      return;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY };
    galleryControl.setPointerCapture(event.pointerId);
  });
  galleryControl.addEventListener("pointermove", (event) => {
    if (!drag || drag.id !== event.pointerId) return;
    turnGallery((event.clientX - drag.x) * -0.004);
    if (event.pointerType !== "touch") {
      galleryPitchTarget = THREE.MathUtils.clamp(
        galleryPitchTarget + (event.clientY - drag.y) * 0.003,
        -0.45,
        0.45,
      );
    }
    drag.x = event.clientX;
    drag.y = event.clientY;
  });
  const release = () => {
    drag = undefined;
  };
  galleryControl.addEventListener("pointerup", release);
  galleryControl.addEventListener("pointercancel", release);
  galleryControl.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      turnGallery(event.key === "ArrowLeft" ? -0.35 : 0.35);
    }
  });
  galleryControl
    .querySelectorAll("button")
    .forEach((button, index) =>
      button.addEventListener("click", () =>
        turnGallery(index === 0 ? -0.45 : 0.45),
      ),
    );
  let frame = 0;
  let disposed = false;
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance",
    });
  } catch {
    root.dataset.static = "";
    status.textContent = "3D unavailable. The full story is below.";
    toggle.hidden = true;
    return;
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
  camera.position.set(0, 0, 10);
  const environment = new RoomEnvironment();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envMap = pmrem.fromScene(environment, 0.04);
  scene.environment = envMap.texture;
  environment.dispose();
  pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x73786c, 1.5));
  const key = new THREE.DirectionalLight(0xfff8ed, 3);
  key.position.set(-3, 5, 5);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xd6e0df, 2);
  rim.position.set(4, 1, -3);
  scene.add(rim);
  const laptop = new THREE.Group();
  const rig = new THREE.Group();
  scene.add(laptop, rig);
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  const resources = new Set<
    THREE.BufferGeometry | THREE.Material | THREE.Texture
  >();
  function own(model: THREE.Object3D) {
    model.traverse((o) => {
      if (!(o instanceof THREE.Mesh)) return;
      resources.add(o.geometry);
      for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
        resources.add(m);
        for (const v of Object.values(m))
          if (v instanceof THREE.Texture) resources.add(v);
      }
    });
  }
  async function model(path: string) {
    const { scene: object } = await loader.loadAsync(path);
    own(object);
    if (disposed) {
      for (const r of resources) r.dispose();
      throw new Error("Scene disposed");
    }
    return object;
  }
  function normalize(object: THREE.Object3D, width: number) {
    const box = new THREE.Box3().setFromObject(object);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    object.position.sub(center);
    const wrapper = new THREE.Group();
    wrapper.add(object);
    wrapper.scale.setScalar(width / size.x);
    return wrapper;
  }
  // x, y, z, pitch, yaw, roll, scale; hold a shot before moving to the next.
  const laptopPoses = [
    [1.85, -0.05, 0, 0.2, -0.58, -0.09, 0.8],
    [1.95, -0.05, -0.5, 0.22, -0.28, 0.02, 0.78],
    [1.95, -0.05, -0.5, 0.22, -0.28, 0.02, 0.78],
    [7, -3, -5, 0.8, -1.2, -0.2, 0.1],
    [-7, -3, -5, 0.4, 0.8, -0.2, 0.1],
  ];
  const cameraPoses = [
    [7, -2, -5, 0.1, -0.6, 0.15, 0.1],
    [7, -2, -5, 0.1, -0.6, 0.15, 0.1],
    [5, 0, -3, 0.1, -1.2, 0.1, 0.4],
    [1.85, -0.15, 0, 0.08, -0.36, -0.05, 1.1],
    [1.5, -0.1, 0.1, 0.04, -0.12, 0, 1.1],
  ];
  let screen: THREE.Mesh | undefined;
  let lid: THREE.Group | undefined;
  let projectTexture: THREE.Texture | undefined;
  let rearScreen: THREE.Mesh | undefined;
  const screenAnchor = new THREE.Vector3();
  let screenWidth = 1;
  new THREE.TextureLoader().load(quilliumScreen, (texture) => {
    if (disposed) {
      texture.dispose();
      return;
    }
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.flipY = false;
    projectTexture = texture;
    resources.add(texture);
    schedule();
  });
  const clamp = THREE.MathUtils.clamp;
  const mix = THREE.MathUtils.lerp;
  let target = 0;
  let current = 0;
  let mobile = innerWidth < 761;
  function locate() {
    if (staticMode) return 0;
    const y = scrollY;
    // Reveal the next fixed scene while the preceding document section leaves.
    const cameraStart = cameraSection.offsetTop;
    if (y >= cameraStart - innerHeight && y < cameraStart) {
      return mix(
        2.84,
        3,
        clamp((y - cameraStart + innerHeight) / innerHeight, 0, 1),
      );
    }
    let index = 0;
    for (let i = 0; i < chapters.length; i++)
      if (y >= chapters[i].offsetTop) index = i;
    const start = chapters[index].offsetTop;
    const duration = chapters[index].offsetHeight;
    return (
      Number(chapters[index].dataset.scene) +
      clamp((y - start) / duration, 0, 1)
    );
  }
  function pose(group: THREE.Group, poses: number[][], value: number) {
    const index = Math.min(Math.floor(value), poses.length - 1);
    const next = Math.min(index + 1, poses.length - 1);
    const t = THREE.MathUtils.smoothstep(value - index, 0.38, 1);
    const p = poses[index].map((n, i) => mix(n, poses[next][i], t));
    if (mobile) {
      p[0] *= 0.12;
      p[1] = mix(p[1], -1.5, 0.75);
      p[6] *= 0.49;
      if (value < 1) {
        p[0] = mix(0.1, 1.95 * 0.12, t);
        p[1] = mix(-1.1, mix(-0.05, -1.5, 0.75), t);
        p[6] = mix(0.41, 0.78 * 0.49, t);
      }
    }
    group.position.set(p[0], p[1], p[2]);
    group.rotation.set(p[3], p[4], p[5]);
    group.scale.setScalar(p[6]);
  }
  // A real inward-facing gallery is rendered into the LCD before entering it.
  const galleryScene = new THREE.Scene();
  galleryScene.background = new THREE.Color(0x111827);
  const galleryCamera = new THREE.PerspectiveCamera(65, 1, 0.1, 60);
  const galleryTarget = new THREE.WebGLRenderTarget(1024, 768);
  const dome = new THREE.Mesh(
    new THREE.SphereGeometry(16, 40, 24),
    new THREE.MeshBasicMaterial({
      color: 0x23324b,
      side: THREE.BackSide,
      wireframe: true,
      transparent: true,
      opacity: 0.13,
    }),
  );
  const floor = new THREE.GridHelper(40, 20, 0x34435e, 0x202d43);
  floor.position.y = -6;
  galleryScene.add(floor);
  resources.add(floor.geometry);
  for (const material of Array.isArray(floor.material)
    ? floor.material
    : [floor.material])
    resources.add(material);
  galleryScene.add(dome);
  own(dome);
  const galleryImages = Object.values(
    import.meta.glob<string>("../assets/photography/*.webp", {
      eager: true,
      query: "?url",
      import: "default",
    }),
  );
  for (let row = -1; row <= 1; row++) {
    for (let column = -4; column <= 3; column++) {
      const theta = ((column + (row === 0 ? 0 : 0.45)) * Math.PI * 2) / 8;
      const photo =
        galleryImages[(column + 4 + (row + 1) * 8) % galleryImages.length];
      const material = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        side: THREE.DoubleSide,
        toneMapped: false,
      });
      const print = new THREE.Mesh(
        new THREE.PlaneGeometry(3.7, 2.45),
        material,
      );
      const depth = 9 + ((column + 4) % 3) * 1.6 + Math.abs(row) * 1.2;
      print.position.set(
        Math.sin(theta) * depth,
        row * 3.5 + Math.sin(column * 2) * 0.3,
        -Math.cos(theta) * depth,
      );
      print.lookAt(0, 0, 0);
      print.rotateZ(Math.sin(column * 3 + row) * 0.035);
      galleryScene.add(print);
      own(print);
      new THREE.TextureLoader().load(photo, (texture) => {
        if (disposed) {
          texture.dispose();
          return;
        }
        texture.colorSpace = THREE.SRGBColorSpace;
        material.map = texture;
        material.needsUpdate = true;
        resources.add(texture);
        schedule();
      });
    }
  }
  function draw() {
    frame = 0;
    if (disposed || document.hidden) return;
    current = staticMode ? 0 : mix(current, target, 0.15);
    if (Math.abs(current - target) < 0.001) current = target;
    pose(laptop, laptopPoses, current);
    if (lid)
      lid.rotation.x =
        0.42 * (1 - THREE.MathUtils.smoothstep(current, 0, 0.65));
    pose(rig, cameraPoses, current);
    const turn = THREE.MathUtils.smoothstep(current, 3.2, 3.58);
    const zoom = THREE.MathUtils.smoothstep(current, 3.62, 4.02);
    if (current >= 3.2) {
      const baseScale = mobile ? 0.539 : 1.1;
      const finalScale = Math.max(18, (mobile ? 11 : 15) / screenWidth);
      const scale = baseScale * Math.pow(finalScale / baseScale, zoom);
      rig.rotation.set(
        mix(0.08, 0, turn),
        mix(-0.36, -Math.PI, turn),
        mix(-0.05, 0, turn),
      );
      rig.scale.setScalar(scale);
      const anchor = screenAnchor
        .clone()
        .multiplyScalar(scale)
        .applyEuler(rig.rotation);
      rig.position.set(
        mix(mobile ? 0.222 : 1.85, -anchor.x, turn),
        mix(mobile ? -1.16 : -0.15, -anchor.y, turn),
        -anchor.z * zoom,
      );
    }
    if (rearScreen && zoom > 0) {
      rig.updateMatrixWorld(true);
      const geometry = rearScreen.geometry as THREE.PlaneGeometry;
      const halfW = geometry.parameters.width / 2;
      const halfH = geometry.parameters.height / 2;
      const lower = rearScreen
        .localToWorld(new THREE.Vector3(-halfW, -halfH, 0))
        .project(camera);
      const upper = rearScreen
        .localToWorld(new THREE.Vector3(halfW, halfH, 0))
        .project(camera);
      const match = THREE.MathUtils.smoothstep(zoom, 0.25, 0.9);
      const x = mix(1, Math.abs(upper.x - lower.x) / 2, match);
      const y = mix(1, Math.abs(upper.y - lower.y) / 2, match);
      galleryTarget.texture.repeat.set(x, y);
      galleryTarget.texture.offset.set((1 - x) / 2, (1 - y) / 2);
    } else {
      galleryTarget.texture.repeat.set(1, 1);
      galleryTarget.texture.offset.set(0, 0);
    }
    rig.visible = current > 2.55 && current < 4.02;
    galleryCamera.aspect = camera.aspect;
    galleryYaw = mix(galleryYaw, galleryYawTarget, 0.15);
    galleryPitch = mix(galleryPitch, galleryPitchTarget, 0.15);
    galleryCamera.rotation.set(galleryPitch, -galleryYaw, 0, "YXZ");
    galleryCamera.position.set(
      Math.sin(galleryYaw) * 0.5,
      0,
      Math.cos(galleryYaw) * 0.5,
    );
    galleryControl.hidden = staticMode || current < 4.02 || current > 4.42;
    if (galleryControl.hidden) drag = undefined;
    galleryCamera.updateProjectionMatrix();
    renderer.setRenderTarget(galleryTarget);
    renderer.render(galleryScene, galleryCamera);
    renderer.setRenderTarget(null);
    laptop.visible = current < 1.95;
    if (screen && projectTexture) {
      const material = screen.material as THREE.MeshBasicMaterial;
      const texture = projectTexture;
      if (material.map !== texture) {
        material.map = texture;
        material.needsUpdate = true;
      }
    }
    const readingCommunity =
      scrollY > sourceSection.offsetTop - innerHeight * 0.35 &&
      scrollY < cameraSection.offsetTop - innerHeight;
    const indexVisible =
      readingCommunity || scrollY > indexSection.offsetTop - innerHeight * 0.05;
    const laptopFade = 1 - THREE.MathUtils.smoothstep(current, 1.72, 1.95);
    const cameraFade =
      THREE.MathUtils.smoothstep(current, 2.55, 2.85) *
      (1 - THREE.MathUtils.smoothstep(current, 4.42, 4.52));
    canvas.style.opacity = String(
      indexVisible ? 0 : staticMode ? 1 : Math.max(laptopFade, cameraFade),
    );
    const dark = !staticMode && current > 2.78 && !indexVisible;
    root.toggleAttribute("data-dark", dark);
    panels.forEach((panel, panelIndex) => {
      const i = Number(chapters[panelIndex].dataset.scene);
      if (staticMode) {
        panel.style.removeProperty("opacity");
        panel.style.removeProperty("visibility");
        panel.style.removeProperty("transform");
        panel.inert = false;
        return;
      }
      const local = current - i;
      const enter =
        i === 0 ? 1 : THREE.MathUtils.smoothstep(local, -0.16, 0.07);
      const leave =
        1 -
        THREE.MathUtils.smoothstep(
          local,
          i === 4
            ? 0.88
            : i === 1
              ? 0.65
              : i === 3
                ? 0.36
                : i === 2
                  ? 0.8
                  : 0.66,
          i === 1 ? 0.88 : i === 3 ? 0.56 : 0.98,
        );
      const opacity = indexVisible
        ? 0
        : enter *
          leave *
          (i === 4 ? THREE.MathUtils.smoothstep(current, 4.53, 4.64) : 1);
      panel.style.opacity = String(opacity);
      panel.style.visibility = opacity > 0.001 ? "visible" : "hidden";
      panel.style.transform = `translateY(${(1 - enter) * 32 - (1 - leave) * 20}px)`;
      panel.inert = opacity < 0.35;
    });
    const galleryCopyOpacity = staticMode
      ? 1
      : THREE.MathUtils.smoothstep(current, 4.53, 4.64);
    galleryHeading.style.opacity = String(galleryCopyOpacity);
    galleryFoot.style.opacity = String(galleryCopyOpacity);
    prints.forEach((print, i) => {
      const enter = THREE.MathUtils.smoothstep(
        current,
        4.53 + i * 0.015,
        4.62 + i * 0.015,
      );
      print.style.transform = staticMode
        ? "none"
        : `translate(${(i - 1) * (1 - enter) * 180}px,${(1 - enter) * 60}px)`;
    });
    renderer.render(
      current >= 4.02 && !staticMode ? galleryScene : scene,
      current >= 4.02 && !staticMode ? galleryCamera : camera,
    );
    if (
      !staticMode &&
      (Math.abs(current - target) > 0.001 ||
        Math.abs(galleryYaw - galleryYawTarget) > 0.0001 ||
        Math.abs(galleryPitch - galleryPitchTarget) > 0.0001)
    )
      schedule();
  }
  function schedule() {
    if (!frame && !disposed) frame = requestAnimationFrame(draw);
  }
  function onScroll() {
    target = locate();
    if (Math.abs(target - current) > 1.2) current = target;
    schedule();
  }
  function resize() {
    mobile = innerWidth < 761;
    renderer.setSize(innerWidth, innerHeight, false);
    camera.aspect = innerWidth / innerHeight;
    camera.position.z = mobile ? 11.8 : 10;
    camera.updateProjectionMatrix();
    galleryTarget.setSize(
      Math.min(innerWidth, 1600),
      (Math.min(innerWidth, 1600) * innerHeight) / innerWidth,
    );
    onScroll();
  }
  function setMotion() {
    root.toggleAttribute("data-static", staticMode);
    toggle.textContent = staticMode ? "Motion off" : "Motion on";
    toggle.setAttribute("aria-pressed", String(staticMode));
    resize();
  }
  const changeMotion = () => {
    staticMode = !staticMode;
    setMotion();
  };
  const preferenceChange = () => {
    staticMode = reduced.matches;
    setMotion();
  };
  const visibilityChange = () => {
    if (!document.hidden) onScroll();
  };
  const chapterStops = [0, 0.08, 0.08, 0.35];
  const chapterNavigation = (event: MouseEvent) => {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const link = (event.target as Element).closest<HTMLAnchorElement>(
      'a[href^="#"]',
    );
    if (!link) return;
    if (link.classList.contains("resume-jump")) {
      event.preventDefault();
      const resume = root.querySelector<HTMLElement>("#index")!;
      history.pushState(null, "", "#index");
      resume.setAttribute("tabindex", "-1");
      resume.focus({ preventScroll: true });
      resume.scrollIntoView({ behavior: "instant", block: "start" });
      return;
    }
    const index = chapters.findIndex(
      (chapter) => `#${chapter.id}` === link.getAttribute("href"),
    );
    if (index < 0 || staticMode) return;
    event.preventDefault();
    history.pushState(null, "", link.getAttribute("href")!);
    window.scrollTo({
      top:
        chapters[index].offsetTop +
        chapters[index].offsetHeight * chapterStops[index],
      behavior: "instant",
    });
  };
  root.addEventListener("click", chapterNavigation);
  toggle.addEventListener("click", changeMotion);
  reduced.addEventListener("change", preferenceChange);
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", resize);
  document.addEventListener("visibilitychange", visibilityChange);
  canvas.addEventListener("webglcontextlost", (event) => {
    event.preventDefault();
    staticMode = true;
    setMotion();
    status.hidden = false;
    status.textContent = "3D paused. The full story is below.";
  });
  root.dataset.cinema = "";
  setMotion();
  const results = await Promise.allSettled([
    model("/models/macbook.glb").then((object) => {
      object.traverse((child) => {
        if (!(child instanceof THREE.Mesh) || child.name !== "VQmfhbMzfNAuKAD")
          return;
        // The display surface from the source model, preserving its authored UVs.
        screen = child;
        const material = new THREE.MeshBasicMaterial({
          map: projectTexture ?? null,
          toneMapped: false,
        });
        child.material = material;
        resources.add(material);
      });
      const displayAssembly = object.getObjectByName("VCQqxpxkUlzqcJI");
      if (displayAssembly?.parent) {
        // Hinge in the source model's centimeter coordinates, before normalization.
        const parent = displayAssembly.parent;
        lid = new THREE.Group();
        lid.position.set(0, -12.4, 0);
        parent.add(lid);
        object.updateMatrixWorld(true);
        lid.attach(displayAssembly);
      }
      laptop.add(normalize(object, 4.9));
      schedule();
    }),
    Promise.all([
      model("/models/gear/r7.glb"),
      model("/models/gear/35.glb"),
      model("/models/gear/adapter.glb"),
    ]).then(([body, lens, adapter]) => {
      for (const object of [body, lens, adapter])
        object.traverse((child) => {
          if (!(child instanceof THREE.Mesh)) return;
          for (const material of Array.isArray(child.material)
            ? child.material
            : [child.material]) {
            if (material instanceof THREE.MeshStandardMaterial) {
              material.envMapIntensity = 0.65;
              if (material.normalMap) material.normalScale.multiplyScalar(0.25);
            }
          }
        });
      // The authored rear display determines the portal's actual position and size.
      body.updateMatrixWorld(true);
      body.traverse((child) => {
        if (!(child instanceof THREE.Mesh)) return;
        const materials = Array.isArray(child.material)
          ? child.material
          : [child.material];
        if (
          !materials.some((material) => /R7 display glass/i.test(material.name))
        )
          return;
        const bounds = new THREE.Box3().setFromObject(child);
        const size = bounds.getSize(new THREE.Vector3());
        const center = bounds.getCenter(new THREE.Vector3());
        const geometry = new THREE.PlaneGeometry(size.x * 0.96, size.y * 0.94);
        const material = new THREE.MeshBasicMaterial({
          map: galleryTarget.texture,
          toneMapped: false,
        });
        rearScreen = new THREE.Mesh(geometry, material);
        rearScreen.position.set(center.x, center.y, bounds.min.z - 0.003);
        rearScreen.rotation.y = Math.PI;
        body.add(rearScreen);
        resources.add(geometry);
        resources.add(material);
      });
      const assembly = new THREE.Group();
      adapter.position.z = 0.53;
      lens.position.z = 0.53 - 0.088 + 24 / 55;
      assembly.add(body, lens, adapter);
      rig.add(normalize(assembly, 3.1));
      rig.updateMatrixWorld(true);
      if (rearScreen) {
        rearScreen.getWorldPosition(screenAnchor);
        rig.worldToLocal(screenAnchor);
        const size = new THREE.Box3()
          .setFromObject(rearScreen)
          .getSize(new THREE.Vector3());
        screenWidth = size.x / rig.scale.x;
      }
      schedule();
    }),
  ]);
  if (disposed) return;
  if (results.every((result) => result.status === "fulfilled")) {
    status.hidden = true;
    root.dataset.models = "ready";
  } else {
    status.textContent =
      "Some 3D assets could not load. You can still explore the work.";
    root.dataset.models = "partial";
  }
  onScroll();
  function dispose() {
    disposed = true;
    galleryControl.remove();
    cancelAnimationFrame(frame);
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", resize);
    document.removeEventListener("visibilitychange", visibilityChange);
    reduced.removeEventListener("change", preferenceChange);
    toggle.removeEventListener("click", changeMotion);
    root.removeEventListener("click", chapterNavigation);
    for (const resource of resources) resource.dispose();
    galleryTarget.dispose();
    envMap.dispose();
    renderer.dispose();
  }
  document.addEventListener("astro:before-swap", dispose, { once: true });
  window.addEventListener(
    "pagehide",
    (event) => {
      if (!event.persisted) dispose();
    },
    { once: true },
  );
}
