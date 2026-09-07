import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { HDRLoader } from 'three/addons/loaders/HDRLoader.js';
import { WebGLPathTracer, DenoiseMaterial } from 'three-gpu-pathtracer';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';

const status = document.querySelector<HTMLDivElement>('#status')!;
async function run() {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#111111');
    scene.environment = await new HDRLoader().loadAsync('/models/gear/studio.hdr');
    scene.environment.mapping = THREE.EquirectangularReflectionMapping;
    scene.environmentIntensity = 0.15;
    scene.environmentRotation.y = 0.8;
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    for (const [id, z] of [['r7', 0], ['adapter', 0.53], ['28-135', 0.53 - 0.088 + 24 / 55]] as const) {
        const { scene: model } = await loader.loadAsync(`/models/gear/${id}.glb`);
        model.position.z = z;
        model.traverse(object => {
            if (!(object instanceof THREE.Mesh)) return;
            object.castShadow=true;object.receiveShadow=true;
            // Normalize quantized GLTF attributes before the tracing BVH flattens them.
            const geometry: THREE.BufferGeometry = object.geometry;
            for (const [name, attribute] of Object.entries(geometry.attributes)) {
                if (!attribute.normalized) continue;
                const data = new Float32Array(attribute.count * attribute.itemSize);
                for (let i=0;i<attribute.count;i++) for(let k=0;k<attribute.itemSize;k++) {
                    data[i*attribute.itemSize+k] = k===0 ? attribute.getX(i) : k===1 ? attribute.getY(i) : k===2 ? attribute.getZ(i) : attribute.getW(i);
                }
                object.geometry.setAttribute(name,new THREE.Float32BufferAttribute(data,attribute.itemSize));
            }
            for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
                if (material instanceof THREE.MeshStandardMaterial && material.normalMap) {
                    material.normalMap = material.normalMap.clone();
                    material.normalMap.wrapS = material.normalMap.wrapT = THREE.RepeatWrapping;
                    const rubber = /Pebbled rubber|Scanned grip rubber/.test(material.name);
                    const grain = material.name.includes("Scanned grip rubber") ? 1.25 : material.name.includes("Crinkle painted metal") ? 6 : rubber ? 3 : 5;
                    material.normalMap.repeat.setScalar(grain);
                    material.normalScale.multiplyScalar(rubber ? 0.8 : 0.6);
                    if (rubber) for (const map of [material.roughnessMap, material.metalnessMap]) {
                        if (!map) continue;
                        map.wrapS = map.wrapT = THREE.RepeatWrapping;
                        map.repeat.setScalar(grain);
                    }
                }
                if (material instanceof THREE.MeshPhysicalMaterial && material.transmission > 0) {
                    object.castShadow=false;
                    material.clearcoat = 0;
                    material.color.setRGB(0.98, 0.99, 0.98);
                    material.roughness = 0.015;
                    material.side = THREE.FrontSide;
                    material.thickness = 0.1;
                }
            }
        });
        scene.add(model);
    }
    RectAreaLightUniformsLib.init();
    for (const [color,intensity,width,height,x,y,z] of [
        ['#fff4e6',4,3,4,-3,4,5],
        ['#cbdfff',3,2,4,4,2,-3],
        ['#ffffff',1,1,3,2,1,5],
    ] as const) {
        const light=new THREE.RectAreaLight(color,intensity,width,height);
        light.position.set(x,y,z);light.lookAt(0,0,0.8);scene.add(light);
    }
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(30,30), new THREE.MeshStandardMaterial({color:0x151515,roughness:0.8}));
    floor.receiveShadow=true;floor.rotation.x=-Math.PI/2;floor.position.y=-0.8;scene.add(floor);
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
    camera.position.set(-3.5,1.5,6.4);camera.lookAt(-0.1,0,0.85);
    const raster = new THREE.WebGLRenderer({canvas:document.querySelector<HTMLCanvasElement>('#raster')!,antialias:true});
    const renderer = new THREE.WebGLRenderer({canvas:document.querySelector<HTMLCanvasElement>('#traced')!,antialias:true});
    for (const r of [raster,renderer]) {r.setSize(600,600);r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;r.toneMapping=THREE.AgXToneMapping;r.toneMappingExposure=1;}
    const tracer = new WebGLPathTracer(renderer);
    tracer.bounces=16;tracer.renderScale=0.75;tracer.minSamples=1;tracer.fadeDuration=0;tracer.renderDelay=0;tracer.filterGlossyFactor=0.25;
    const denoise = new DenoiseMaterial({sigma:2,kSigma:1,threshold:0.025});
    const output = new FullScreenQuad(denoise);
    tracer.renderToCanvasCallback=(target,r)=>{denoise.map=target.texture;output.render(r);};
    status.textContent='Building tracing scene…';
    await tracer.setScene(scene,camera);
    (window as any).renderStudy={tracer,renderer,scene,camera,THREE};
    let paused=false;let start=performance.now();
    const view = (front:boolean) => {camera.position.set(front?0:-3.5,front?0.2:1.5,front?7:6.4);camera.lookAt(-0.1,0,0.85);tracer.updateCamera();start=performance.now();};
    document.querySelector('#front')!.addEventListener('click',()=>view(true));
    document.querySelector('#angle')!.addEventListener('click',()=>view(false));
    document.querySelector('#pause')!.addEventListener('click',()=>paused=!paused);
    function frame() {
        requestAnimationFrame(frame);
        if (paused || tracer.samples>=512) return;
        raster.render(scene,camera);tracer.renderSample();
        status.textContent=`${tracer.samples.toFixed(1)} samples · ${((performance.now()-start)/1000).toFixed(1)} seconds`;
        document.documentElement.dataset.samples=String(tracer.samples);
    }
    frame();
}
run().catch(error=>{status.textContent=String(error);console.error(error);});
