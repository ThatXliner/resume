<script>
  let boundingRef;
  export let ariaRole = "region";
  export let perspective = "40px";
</script>

<div style:perspective>
  <div
    class="transition-transform ease-out hover:[transform:rotateX(var(--x-rotation))_rotateY(var(--y-rotation))_scale(1.1)]"
    role={ariaRole}
    on:mouseleave={() => (boundingRef = null)}
    on:mouseenter={(ev) => {
      boundingRef = ev.currentTarget.getBoundingClientRect();
    }}
    on:mousemove={(ev) => {
      if (!boundingRef) return;
      const x = ev.clientX - boundingRef.left;
      const y = ev.clientY - boundingRef.top;
      const xPercentage = x / boundingRef.width;
      const yPercentage = y / boundingRef.height;
      const xRotation = (xPercentage - 0.5) * 20;
      const yRotation = (0.5 - yPercentage) * 20;

      ev.currentTarget.style.setProperty("--x-rotation", `${yRotation}deg`);
      ev.currentTarget.style.setProperty("--y-rotation", `${xRotation}deg`);
      ev.currentTarget.style.setProperty("--x", `${xPercentage * 100}%`);
      ev.currentTarget.style.setProperty("--y", `${yPercentage * 100}%`);
    }}
  >
    <slot />
  </div>
</div>
