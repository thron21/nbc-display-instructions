# v5 build: greyer colours, sub-steps of 14

Same 5,137-piece model as the main booklet, with these changes:

* **Mountains:** white is kept on upward-facing surfaces (more of it higher up); white on side faces and many low
  ledges is now light or dark bluish grey, and about half the visible black pieces are dark bluish grey.
* **Courtyard:** pavers are now about 50% light bluish grey, 37% dark bluish grey, 10% dark red, 3% reddish brown.
* **Hidden fillers:** 10 lime pieces that showed through gaps from the booklet camera are now white or grey.
* **Sub-steps:** at most 14 pieces each (418 sub-steps). The picture stays pinned at the top while you scroll a tick list.
* Ticks are saved under the prefix `nbcdisp4`, separate from the main booklet.

Pictures were rendered with three.js (`source/r3.py`, `source/render_page.html`) using the kit's camera, instead of LeoCAD.
`source/recol2.py` is the colour pass; `source/build_nbc.py` builds the booklet from `source/nbc_display_v5_steps.ldr`.
