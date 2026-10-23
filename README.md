# Song A Day object

A component-based industrial-design study for a collectible that loops one permanently assigned Song A Day video. One exposed button toggles sound while the picture continues. Six Blender concepts explore a monolith, cube, horizontal block, wood cabinet, solar wedge, and powered plinth.

This is a design and sourcing study. There is no finished circuit, firmware, acoustically tested enclosure, or fabrication-ready CAD yet. All screen imagery is an original illustrative singer-and-guitar bitmap, not an actual Song A Day video.

## View and reproduce

Generated images, the illustrated sourcing PDF, and the editable `.blend` file are delivered with the local design package. They are excluded from Git. This hardware concept has no live deployed URL.

With Blender 4.5 or newer, run from the repository root:

```sh
blender -b --python blender/build_concepts.py -- --out renders --samples 48 --resolution 1600
```

Use `--only 01_Monolith` for one render, or `--no-render` to build only the editable Blender file. The file contains six individual concept scenes, an exploded envelope study and a shelf context. All textures are procedural or packed. Units are metres, with millimetres shown in the UI.

Create the PDF and comparison image after rendering:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 build_report.py
```

There are no API keys or environment variables. The renderer uses Metal if available and otherwise falls back to CPU.

## Sourcing assumptions

`research/components.csv` links every named part to a source. `research/sources.json` records price and availability qualifications as checked on October 23, 2026. Prices are USD and exclude taxes, freight and tariffs. Some manufacturer prices were available only in indexed listings; those are labelled. Planning allowances are not supplier quotes. The custom-controller reference part was out of stock at DigiKey when checked.

The cheapest near-term proof uses the Waveshare 2.8-inch non-touch board with its supplied speaker. A larger 40 mm speaker is an optional sound experiment. The custom 100-unit baseline uses a smaller 2.4-inch panel and totals about $31 including estimated assembly and basic packaging, before freight, tax, development, tooling and contingency. That is a planning estimate, not a verified sub-$30 manufacturing offer.

Indoor solar does not support the intended continuous playback at the estimated loads. The solar concept includes battery storage and needs a power-path charger, a suitable 5 V boost stage, temperature sensing and USB backup. It is above the price target. The wired and contact-plinth concepts can omit batteries entirely.

## License

The Python source is GPL-3.0-or-later, copyright 2026 Jonathan Mann, because the modeling scripts use Blender's `bpy` API. This follows [Blender's published Python-script licensing guidance](https://www.blender.org/about/license/). Original geometry, bitmap illustration and generated render artwork are CC BY 4.0; credit Jonathan Mann (Song A Day). See `ASSETS.md`. Supplier products, names and linked documentation retain their owners' rights.
