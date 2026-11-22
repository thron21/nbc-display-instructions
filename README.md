# Nightmare Before Christmas display: building instructions

Interactive, iPad-friendly building instructions for the full 64 x 48 NBC display (v4): the foundation of
12 Technic 16 x 16 bricks pinned together, the plates, snow strip and road, the sideways-masonry courtyard paving, the mountains (layer by layer, peak by peak),
the toy shop niche span and the spiral platform.

**Open the instructions:** https://thron21.github.io/nbc-display-instructions/

* 5,137 parts in 118 steps (155 sub-steps of up to 55 pieces), in 8 sections:
  1. Foundation: Technic bricks and pins
  2. Snow, road and anchors
  3. Courtyard paving
  4. Mountains: layers 1-4
  5. Mountains: layers 5-8
  6. Mountains: layers 9-12
  7. Mountains: layers 13-16, niche span and spiral platform
  8. Mountains: layers 17-25, the peaks
* The **tan 6 x 6 plate** in the last step is only a **placeholder** that marks where the 21351 spiral sits.
  It is not a part to buy.
* **Lime pieces are hidden fillers.** 847 pieces (mostly light bluish grey bricks inside the mountains, under them,
  and under the road tiles) have no face that shows in the finished display, so they are drawn in Lime: build them in
  any colour you have spare. The Parts panel says so on every step that has lime pieces. Found with a voxel check
  (4 LDU grid, flood fill of the outside air; slopes count only by their flat base): a piece is lime when none of its
  faces touches outside air. The foundation, pins, pavers, rock-face pieces, slopes and the tan marker keep their colours.
  By part: 317 x 3005, 273 x 3001, 122 x 3010, 101 x 3004, 12 x 3622, 10 x 3003, 6 x 3002, 5 x 3623, 1 x 4282.
* **Foundation:** one step per white 65803 Technic brick, together with the black 2780 pins that go into its left
  side and front edge (they show up in the picture sticking out of the brick). Build the back row first, right to left.
  A brick can't be pushed onto pins from two sides at once, so put the middle row together next to the back row, then
  push the whole row onto the back row's front pins. Do the same with the front row.
* Each picture shows the new pieces in colour inside a red box, with everything built earlier in pale grey.
  Tick each piece as you place it; the next one glows yellow. Each row says where the piece goes
  (*col* from the left edge, *row* from the front edge).
* **3D** on any picture lets you turn the model with your finger. The 3D files only load the first time you use it.
* **Step by step** shows one sub-step at a time. Swipe the picture to move on.
* **Parts** (tab on the right, or swipe in from the right edge) lists the pieces for the step with quantities.
* **Build in 3D** fills the screen with the 3D model. Put the glowing piece on and tap **Placed ✓**. Swipe in from
  the left edge for a quick tick list. When a step is finished, the next one opens.

Ticks are saved in your browser (key prefix `nbcdisp3`; ticks from older versions of this booklet don't carry over).

The model is the same 5,137 parts as `mountains_v4_full.ldr` (with the hidden pieces in Lime, `mountains_v4_lime.ldr`), regrouped into booklet steps by
`source/make_steps.py`. That script checks that every piece connects to something already built when it's placed
(studs, or a pin in a Technic hole).
The step file, config and the hidden-piece check (`hidden.py`, `hidden.json`) are in `source/`.

Made with the [MOC instruction kit](https://github.com/thron21/moc-instruction-kit).
