# Nightmare Before Christmas display: building instructions

Interactive, iPad-friendly building instructions for the full 64 x 48 NBC display (**v5, hollow mountains**): the
foundation of 12 Technic 16 x 16 bricks pinned together, the plates, snow strip and road, the sideways-masonry
courtyard paving, the mountains (layer by layer, peak by peak), the toy shop niche span and the spiral platform.

**Open the instructions:** https://thron21.github.io/nbc-display-instructions/

* 4,789 parts in 117 steps (390 sub-steps of up to 14 pieces), in 8 sections:
  1. Foundation: Technic bricks and pins
  2. Snow, road and anchors
  3. Courtyard paving
  4. Mountains: layers 1-4
  5. Mountains: layers 5-8
  6. Mountains: layers 9-12
  7. Mountains: layers 13-16, niche span and spiral platform
  8. Mountains: layers 17-25, the peaks
* **Hollow mountains.** The solid hidden filler inside the mountains is gone (v4 had 5,137 parts). Inside each
  mountain only the support pillars that hold up the courses above are built, mostly 2 x 4 bricks, each piece over the
  hollow gripping at least 2 studs where there is room. The outside looks exactly the same as before.
* **Colours** are the greyer v5 colours (white kept on upward-facing surfaces, side faces and low ledges in light or
  dark bluish grey, about half the visible black in dark bluish grey; courtyard pavers mostly light and dark bluish grey).
* The **tan 6 x 6 plate** in the last step is only a **placeholder** that marks where the 21351 spiral sits.
  It is not a part to buy.
* **Lime pieces are hidden.** 497 pieces (mostly the inner support pillars, plus a few plates under the road tiles and
  one niche-span plate) have no face that shows in the finished display, so they are drawn in Lime: build them in any
  colour you have spare. The Parts panel says so on every step that has lime pieces. Found with a voxel check
  (4 LDU grid, flood fill of the outside air; slopes count only by their flat base).
  By part: 393 x 3001, 40 x 3010, 13 x 3002, 13 x 3004, 11 x 3622, 10 x 3003, 8 x 3005, 5 x 3623, 2 x 3020, 1 x 4282, 1 x 3034.
* **Foundation:** one step per white 65803 Technic brick, together with the black 2780 pins that go into its left
  side and front edge. Build the back row first, right to left. Put the middle row together next to the back row,
  then push the whole row onto the back row's front pins. Do the same with the front row.
* Each picture shows the new pieces in colour inside a red box, with everything built earlier in pale grey, and
  stays pinned at the top while you scroll the tick list. Tick each piece as you place it; the next one glows yellow.
* **All parts** (tab at the top of the screen) lists every piece in the booklet grouped by colour (Lime last), with
  how many are placed from your ticks; filter by whole build or the section in view, and "still needed only".
* **Parts** (tab on the left, or swipe in from the left edge) lists the pieces for the step with quantities.
* **3D** on any picture lets you turn the model with your finger. **Step by step** shows one sub-step at a time.
* **Build in 3D** fills the screen with the 3D model. Put the glowing piece on and tap **Placed ✓**. Swipe in from
  the right edge for the tick list.

Ticks are saved in your browser (key prefix `nbcdisp5`; ticks from older versions of this booklet don't carry over).

The model is `mountains_v5_hollow_full.ldr` (hidden pieces in Lime: `mountains_v5_hollow_lime.ldr`), regrouped into
booklet steps by `source/make_steps.py`, which checks that every piece connects to something already built when it's
placed. `source/hollow.py` builds the hollow model from v4; `hidden.py`, `hidden.json` and `lime.json` are the
hidden-piece check. The earlier solid greyer build is kept in [`v5/`](v5/) (5,137 parts, ticks prefix `nbcdisp4`).

Made with the [MOC instruction kit](https://github.com/thron21/moc-instruction-kit).
