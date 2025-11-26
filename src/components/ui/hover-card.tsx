import { useRef } from "react";

export default function TiltContainer({
  ariaRole = "region",
  perspective = "40px",
  children,
}) {
  const boundingRef = useRef(null);

  const handleMouseEnter = (e) => {
    boundingRef.current = e.currentTarget.getBoundingClientRect();
  };

  const handleMouseLeave = () => {
    boundingRef.current = null;
  };

  const handleMouseMove = (e) => {
    if (!boundingRef.current) return;

    const rect = boundingRef.current;
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const xPct = x / rect.width;
    const yPct = y / rect.height;

    const xRotation = (xPct - 0.5) * 20;
    const yRotation = (0.5 - yPct) * 20;

    const el = e.currentTarget;
    el.style.setProperty("--x-rotation", `${yRotation}deg`);
    el.style.setProperty("--y-rotation", `${xRotation}deg`);
    el.style.setProperty("--x", `${xPct * 100}%`);
    el.style.setProperty("--y", `${yPct * 100}%`);
  };

  return (
    <div style={{ perspective }} className="m-3">
      <div
        className="transition-transform ease-out hover:[transform:rotateX(var(--x-rotation))_rotateY(var(--y-rotation))_scale(1.1)]"
        role={ariaRole}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onMouseMove={handleMouseMove}
      >
        {children}
      </div>
    </div>
  );
}
