import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import * as THREE from "three";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { createWebGLCanvas, isLowPowerDevice } from "./capabilities";

export function Backdrop() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fallback = useRef<HTMLDivElement>(null);
  const { pathname } = useLocation();
  useEffect(() => {
    const canvas = canvasRef.current;
    const fallbackNode = fallback.current;
    if (!canvas || !fallbackNode) return;
    const device = navigator as Navigator & { deviceMemory?: number };
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      isLowPowerDevice(device.deviceMemory, device.hardwareConcurrency)) {
      fallbackNode.hidden = false;
      canvas.hidden = true;
      return;
    }
    const cleanup = createWebGLCanvas(canvas, (element) => {
      const renderer = new THREE.WebGLRenderer({ canvas: element, alpha: true, antialias: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(window.innerWidth, window.innerHeight);
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 100);
      camera.position.z = 8;
      const positions = new Float32Array(180 * 3);
      for (let i = 0; i < 180; i += 1) {
        positions[i * 3] = (Math.random() - 0.5) * 15;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 9;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 5;
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const material = new THREE.PointsMaterial({ color: 0x66734f, size: 0.025, transparent: true, opacity: 0.75 });
      const points = new THREE.Points(geometry, material);
      scene.add(points);
      gsap.registerPlugin(ScrollTrigger);
      const story = document.querySelector(".story-scroll");
      const storyTimeline = story ? gsap.timeline({
        scrollTrigger: { trigger: story, start: "top top", end: "bottom bottom", scrub: 1 },
      }).to(camera.position, { z: 4.5, ease: "none" }, 0).to(points.scale, { x: 1.6, y: 1.6, z: 1.6, ease: "none" }, 0.45) : null;
      let frame = 0;
      let running = true;
      const draw = () => {
        if (!running) return;
        points.rotation.y += 0.0004;
        renderer.render(scene, camera);
        frame = window.requestAnimationFrame(draw);
      };
      draw();
      const resize = () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      };
      window.addEventListener("resize", resize);
      return { dispose: () => {
        running = false;
        window.cancelAnimationFrame(frame);
        window.removeEventListener("resize", resize);
        geometry.dispose();
        material.dispose();
        storyTimeline?.scrollTrigger?.kill();
        storyTimeline?.kill();
        renderer.dispose();
      } };
    });
    fallbackNode.hidden = Boolean(cleanup);
    if (!cleanup) canvas.hidden = true;
    return cleanup ?? undefined;
  }, [pathname]);
  return <><canvas ref={canvasRef} className="backdrop-canvas" aria-hidden="true" /><div ref={fallback} className="backdrop-fallback" hidden aria-hidden="true" /></>;
}
