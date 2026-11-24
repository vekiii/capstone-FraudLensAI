# Feature 06 — Predaja nakon T001, 21. novembar 2026.

T001 je završen na grani `006-capstone-evaluation`, revizija
`cbfa969ca34f9d19c72b39a662f3e125e4f373d4`. Obe zaključane instalacije su
uspele. Prvi `npm ci` vratio je EACCES u sandboxu, a ponavljanje uz eskalaciju
je prošlo. Backend 84/84, React 47/47, typecheck i build prolaze. Ostaju
Starlette/httpx deprecation upozorenje i Vite upozorenje o Three.js chunk-u.

[Komande i rezultati](feature-006-setup.md).
Puna regresija i ljudska reprodukcija nisu deo izvršenog baseline-a.
Sledeći korak je provera T098 artefakata u T002, u zasebnoj fazi T002–T003.
