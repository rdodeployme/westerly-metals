# Westerly Metals site source

Static site for Westerly Metals (scrap metal drop-off, Atkinsons Road, Moorabool; open 6am to 6pm, 7 days).

- Edit pages in `src/pages/*.html`, styles in `src/css/main.css`, behaviour in `src/js/main.js`.
- Rebuild into the repo root: `python3 _build/build.py` (needs Python 3, Pillow and cairosvg).
- `data/towns.json`: road distances and drive times (OSRM, OpenStreetMap) from each town to the yard, to the Laverton North yards (Dohertys Road) and to Sims Geelong.
- `brand/concepts.py` builds the grab-claw logo (`grab()`); outputs live in `assets/brand/`.
- Rules: no em dashes, no "free", Australian English. The build fails if either slips in.
