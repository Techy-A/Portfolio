"""Manim scenes for the Method section (Fig. 3 and Fig. 4).

What: two short explanatory animations, rendered once and committed as video in media/.
  FoldLeak   - random folds put a speaker's twin clip on both sides of a fold; speaker-grouped folds do not.
  GatePush   - an unimportant pruning gate under the L1 and the L2 penalty alone: L1 crosses the 0.01
               pruning threshold, L2's push fades as the gate nears zero (gradients from the project README).
Why: these two decisions are mathematical and had no figure; an animation shows the mechanism, not just the verdict.
Style: the site's palette on pure black (the page blends black away; the light theme inverts it), Space Mono text,
       no LaTeX so the render needs only Manim, Cairo, Pango and the Space Mono font.

Usage (from the repo root, Manim Community 0.19+ and Space Mono installed):
  python src/manim/render.py          # renders both scenes, then encodes media/*.mp4 and *.webp posters
"""
import numpy as np
from manim import (Axes, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Scene, Text, ValueTracker,
                   VGroup, always_redraw, config, linear, LEFT, RIGHT, UP, DOWN, UL, UR, DL)

INK, INK3, GOLD, SAGE, ROSE = "#ECE9E3", "#8E8A82", "#D9B26F", "#9DC4AF", "#D8A3A0"
FONT = "Space Mono"
config.background_color = "#000000"
config.pixel_width, config.pixel_height = 1280, 640
config.frame_width, config.frame_height = 14.2, 7.1


def label(text, size=22, color=INK3, weight="NORMAL"):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


class FoldLeak(Scene):
    """Eight speakers, two clips each, placed in speaker-embedding space (twins sit close together)."""

    def construct(self):
        rng = np.random.default_rng(3)
        centres = [np.array([x, y, 0]) for x, y in
                   [(-4.6, 1.3), (-2.4, -1.1), (-0.6, 1.6), (1.2, -0.9), (3.1, 1.2), (4.9, -1.2), (-4.0, -1.6), (2.4, 2.4)]]
        clips, owner = [], []
        for s, c in enumerate(centres):
            a = rng.uniform(0, np.pi)                    # a speaker's two clips sit close, never on top of each other
            for sign in (1, -1):
                clips.append(c + sign * .34 * np.array([np.cos(a), np.sin(a), 0]))
                owner.append(s)
        dots = VGroup(*[Circle(radius=.17, color=INK, stroke_width=3).move_to(p) for p in clips])
        title = label("8 speakers x 2 clips, placed by voice", 22).to_corner(UL, buff=.35)
        key = VGroup(VGroup(Circle(radius=.11, color=INK, stroke_width=3), label("train", 20)).arrange(RIGHT, buff=.15),
                     VGroup(Circle(radius=.11, color=GOLD, fill_color=GOLD, fill_opacity=1),
                            label("validation", 20)).arrange(RIGHT, buff=.15)).arrange(RIGHT, buff=.45)
        key.to_corner(UR, buff=.4)
        self.play(FadeIn(title), FadeIn(key), *[Create(d) for d in dots], run_time=1.6)
        self.wait(.4)

        def split(val, name, colour):
            # validation clips fill gold; a gold line marks a twin left behind in training
            head = label(name, 26, colour, "BOLD")
            moves = [d.animate.set_fill(GOLD if i in val else "#000000", opacity=1).set_stroke(GOLD if i in val else INK)
                     for i, d in enumerate(dots)]
            leaks = [i for i in val if any(owner[j] == owner[i] and j not in val for j in range(len(clips)))]
            lines = VGroup(*[Line(clips[i], clips[j], color=GOLD, stroke_width=5)
                             for i in leaks for j in range(len(clips)) if owner[j] == owner[i] and j != i])
            count = label(f"{len(leaks)} of {len(val)} validation clips share a voice with training", 20, colour)
            VGroup(head, count).arrange(DOWN, aligned_edge=LEFT, buff=.12).to_corner(DL, buff=.4)
            return head, moves, lines, count

        head, moves, lines, count = split({1, 5, 8, 12}, "random folds", ROSE)
        self.play(FadeIn(head), *moves, run_time=1.2)
        self.play(*[Create(l) for l in lines], FadeIn(count), run_time=1.2)
        self.wait(2.2)

        head2, moves2, lines2, count2 = split({2, 3, 10, 11}, "speaker-grouped folds", SAGE)
        self.play(FadeOut(lines), FadeOut(head), FadeOut(count), *moves2, run_time=1.2)
        self.play(FadeIn(head2), FadeIn(count2), run_time=.8)
        rings = VGroup(*[Circle(radius=.62, color=SAGE, stroke_width=2).move_to((clips[a] + clips[a + 1]) / 2)
                         for a in (2, 10)])
        self.play(*[Create(r) for r in rings], run_time=.9)
        self.wait(3)


class GatePush(Scene):
    """Gate g = sigmoid(s). Penalty-only push on s: L1 gives g(1-g), L2 gives 2g^2(1-g). Same step size."""

    def construct(self):
        T, lr = 1000, 100 / (0.55 * 1000)               # chosen so the L1 gate crosses 0.01 at 55% of the run
        sig = lambda s: 1 / (1 + np.exp(-s))
        paths = {}
        for name, push in (("L1", lambda g: g * (1 - g)), ("L2", lambda g: 2 * g * g * (1 - g))):
            s, out = 0.0, []
            for _ in range(T + 1):
                g = sig(s); out.append(g); s -= lr * push(g)
            paths[name] = np.array(out)

        ax = Axes(x_range=[0, T, 250], y_range=[0, 3, 1], x_length=10.6, y_length=4.6, tips=False,
                  axis_config={"color": INK3, "stroke_width": 2, "include_ticks": True}).shift(DOWN * .25 + RIGHT * .55)
        ticks = VGroup(*[label(t, 20).next_to(ax.c2p(0, y), LEFT, buff=.2) for t, y in
                         (("1", 3), ("0.1", 2), ("0.01", 1), ("0.001", 0))])
        ylab = label("gate value (log)", 20).next_to(ax, UP, buff=.2).align_to(ax, LEFT).shift(LEFT * .9)
        xlab = label("training steps, penalty only", 20).next_to(ax, DOWN, buff=.25).align_to(ax, RIGHT)
        thr = DashedLine(ax.c2p(0, 1), ax.c2p(T, 1), color=INK3, stroke_width=2, dash_length=.12)
        thr_lab = label("pruning threshold 0.01", 20).next_to(ax.c2p(0, 1), DOWN, buff=.15).align_to(ax.c2p(25, 0), LEFT)
        self.play(Create(ax), FadeIn(ticks), FadeIn(ylab), FadeIn(xlab), run_time=1.2)
        self.play(Create(thr), FadeIn(thr_lab), run_time=.7)

        t = ValueTracker(0)
        f = {k: (lambda p: (lambda x: 3 + np.log10(np.interp(x, np.arange(T + 1), p))))(v) for k, v in paths.items()}
        colour = {"L1": SAGE, "L2": ROSE}
        curves, heads, tags = VGroup(), VGroup(), VGroup()
        for k in ("L2", "L1"):
            curves.add(always_redraw(lambda k=k: ax.plot(f[k], x_range=[0, max(t.get_value(), 1e-3), 4],
                                                         color=colour[k], stroke_width=5)))
            heads.add(always_redraw(lambda k=k: Dot(ax.c2p(t.get_value(), f[k](t.get_value())), radius=.09, color=colour[k])))
            tags.add(always_redraw(lambda k=k: label(k, 24, colour[k], "BOLD").next_to(
                ax.c2p(t.get_value(), f[k](t.get_value())), UR, buff=.08)))
        readout = always_redraw(lambda: label(
            "push on gate score   L1 g(1-g) = %.4f   L2 2g^2(1-g) = %.4f" % (
                paths["L1"][int(t.get_value())] * (1 - paths["L1"][int(t.get_value())]),
                2 * paths["L2"][int(t.get_value())] ** 2 * (1 - paths["L2"][int(t.get_value())])), 20, INK)
            .to_edge(UP, buff=.3).align_to(ax, RIGHT))
        self.add(curves, heads, tags, readout)
        cross = int(np.argmax(paths["L1"] < .01))
        self.play(t.animate.set_value(cross), run_time=5.5, rate_func=linear)
        ring = Circle(radius=.28, color=SAGE, stroke_width=3).move_to(ax.c2p(cross, 1))
        pruned = label("L1: pruned", 22, SAGE, "BOLD").next_to(ring, DOWN, buff=.15)
        self.play(Create(ring), FadeIn(pruned), run_time=.6)
        self.play(t.animate.set_value(T), run_time=3.5, rate_func=linear)
        end = label("L2: g = %.3f, still above the threshold" % paths["L2"][T], 22, ROSE, "BOLD")
        end.align_to(ax.c2p(T, 0), RIGHT).set_y(ax.c2p(0, 2.4)[1])
        self.play(FadeIn(end), run_time=.6)
        self.wait(3)
