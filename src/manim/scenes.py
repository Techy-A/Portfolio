"""Manim scenes: Fig. 1 and Fig. 3 to Fig. 6 in the Method section and one per project card.

What: short explanatory animations, rendered once and committed as video in media/.
  FoldLeak   - random folds put a speaker's twin clip on both sides of a fold; speaker-grouped folds do not.
  GatePush   - an unimportant pruning gate under the L1 and the L2 penalty alone: L1 crosses the 0.01
               pruning threshold, L2's push fades as the gate nears zero (gradients from the project README).
  Rrf, Arena, Listen, Lora, Prune - one idea per project card; Judge, Chain - Fig. 5 and Fig. 6; Retrieval - Fig. 1.
Why: these decisions had no figure; an animation shows the mechanism, not just the verdict.
Style: the site's palette on pure black (the page blends black away; the light theme inverts it), Space Mono text,
       no LaTeX so the render needs only Manim, Cairo, Pango and the Space Mono font.

Usage (from the repo root, Manim Community 0.19+ and Space Mono installed):
  python src/manim/render.py [name ...]   # renders the scenes (all by default), then encodes media/*.mp4 and *.webp posters
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


# ---------------------------------------------------------------- project scenes (one per project card)

class Rrf(Scene):
    """CollegeBot: reciprocal rank fusion, score = sum over retrievers of 1 / (60 + rank) (RRF_K = 60 in rag.py),
    top 8 kept. Passage names are illustrative."""

    def construct(self):
        K, KEEP = 60, 8
        dense = ["fees p.3", "hostel p.7", "admissions p.2", "placements p.12", "fees p.4", "scholarship p.5"]
        sparse = ["admissions p.2", "refunds p.9", "fees p.3", "rules p.1", "hostel p.7", "transport p.6"]
        def column(items, x, title):
            head = label(title, 20, INK, "BOLD").move_to([x, 2.85, 0], aligned_edge=LEFT)
            rows = VGroup(*[label(f"{i + 1}  {t}", 19, INK).move_to([x, 2.05 - i * .62, 0], aligned_edge=LEFT)
                            for i, t in enumerate(items)])
            return head, rows
        dh, dr = column(dense, -6.75, "FAISS, dense")
        sh, sr = column(sparse, -3.45, "BM25, keywords")
        self.play(FadeIn(dh), FadeIn(sh), *[FadeIn(r, shift=RIGHT * .2) for r in [*dr, *sr]], run_time=1.4)
        links = VGroup(*[Line(dr[i].get_right() + RIGHT * .08, sr[j].get_left() + LEFT * .08, color=GOLD, stroke_width=3)
                         for i, a in enumerate(dense) for j, b in enumerate(sparse) if a == b])
        self.play(*[Create(l) for l in links], run_time=1.0)
        self.wait(.5)

        ranks = {}
        for lst in (dense, sparse):
            for r, t in enumerate(lst, 1):
                ranks.setdefault(t, []).append(r)
        score = {t: sum(1 / (K + r) for r in rs) for t, rs in ranks.items()}
        fused = sorted(ranks, key=lambda t: -score[t])
        fh = label("fused: sum of 1 / (60 + rank)", 20, GOLD, "BOLD").move_to([.35, 2.85, 0], aligned_edge=LEFT)
        rows = VGroup()
        for i, t in enumerate(fused):
            both = len(ranks[t]) > 1
            terms = " + ".join(f"1/{K + r}" for r in ranks[t])
            rows.add(VGroup(label(f"{i + 1:>2}  {t}", 18, INK), label(f"{terms} = {score[t]:.4f}", 18, GOLD if both else INK3))
                     .arrange(RIGHT, buff=.3).move_to([.35, 2.2 - i * .5, 0], aligned_edge=LEFT))
        for row in rows:
            row[1].move_to([3.55, row.get_y(), 0], aligned_edge=LEFT)
        self.play(FadeIn(fh), run_time=.5)
        self.play(*[FadeIn(r, shift=LEFT * .3) for r in rows], lag_ratio=.12, run_time=2.2)
        cut = DashedLine([.35, 2.2 - (KEEP - .5) * .5, 0], [6.85, 2.2 - (KEEP - .5) * .5, 0], color=INK3, dash_length=.1)
        cl = label("top 8 go to the model", 18, INK3).move_to([6.85, 2.2 - len(fused) * .5, 0], aligned_edge=RIGHT)
        self.play(Create(cut), FadeIn(cl), *[r.animate.set_opacity(.35) for r in rows[KEEP:]], run_time=.8)
        win = label("passages both retrievers found rise to the top", 20, SAGE, "BOLD").to_edge(DOWN, buff=.35).align_to(dh, LEFT)
        self.play(*[r.animate.set_color(SAGE) for r, t in zip(rows, fused) if len(ranks[t]) > 1], FadeIn(win), run_time=.9)
        self.wait(3.2)


class Arena(Scene):
    """IMAGE-LLP-VISION: 50 images, all pairs = 1,225 matches; 5 prompt groups of 10 = 5 x 45 = 225.
    Then Elo with K = 32 from 1500 (elo_system.py); the match outcomes are illustrative."""

    def construct(self):
        n, c = 50, .082
        origin = np.array([-6.55, 2.3, 0])
        cells, inside = VGroup(), []
        for i in range(n):
            for j in range(i + 1, n):
                cells.add(Dot(origin + np.array([j * c, -i * c, 0]), radius=.031, color=INK3))
                inside.append(i // 10 == j // 10)
        title = label("every pair of 50 images", 20, INK).move_to([-6.75, 2.95, 0], aligned_edge=LEFT)
        count = label("1,225 matches", 22, ROSE, "BOLD").move_to([-6.75, -2.6, 0], aligned_edge=LEFT)
        self.play(FadeIn(title), FadeIn(cells, lag_ratio=.002), run_time=2.0)
        self.play(FadeIn(count), run_time=.5)
        self.wait(.8)
        title2 = label("only within each prompt group", 20, INK).move_to(title, aligned_edge=LEFT)
        count2 = label("5 groups x 45 = 225 matches", 22, SAGE, "BOLD").move_to(count, aligned_edge=LEFT)
        self.play(*[d.animate.set_opacity(.12) for d, k in zip(cells, inside) if not k],
                  *[d.animate.set_color(GOLD) for d, k in zip(cells, inside) if k],
                  FadeOut(title), FadeIn(title2), FadeOut(count), FadeIn(count2), run_time=1.6)
        self.wait(1.0)

        R, names, x0 = {k: 1500.0 for k in "ABCD"}, "ABCD", .55
        y = lambda k: 1.55 - names.index(k) * .72
        head = label("Elo inside one group, K = 32", 20, INK, "BOLD").move_to([x0, 2.95, 0], aligned_edge=LEFT)
        form = label("expected = 1 / (1 + 10^((Rb - Ra) / 400))", 18, INK3).move_to([x0, 2.45, 0], aligned_edge=LEFT)
        bar = lambda k: Line([x0 + .5, y(k), 0], [x0 + .5 + (R[k] - 1400) / 200 * 3.9, y(k), 0], color=GOLD, stroke_width=14)
        num = lambda k: label(f"{R[k]:.0f}", 19, INK).next_to(bar(k), RIGHT, buff=.2)
        tags = VGroup(*[label(k, 20, INK, "BOLD").move_to([x0 + .15, y(k), 0]) for k in names])
        bars, nums = {k: bar(k) for k in names}, {k: num(k) for k in names}
        self.play(FadeIn(head), FadeIn(form), FadeIn(tags), *[FadeIn(b) for b in bars.values()],
                  *[FadeIn(v) for v in nums.values()], run_time=1.0)
        note = None
        for a, b, win in (("A", "B", "A"), ("C", "D", "C"), ("A", "C", "A"), ("B", "D", "D"), ("A", "D", "A"), ("B", "C", "C")):
            e = 1 / (1 + 10 ** ((R[b] - R[a]) / 400))
            s = 1.0 if win == a else 0.0
            R[a] += 32 * (s - e); R[b] -= 32 * (s - e)
            new = label(f"{a} vs {b}: {win} wins", 19, INK3).move_to([x0, -1.5, 0], aligned_edge=LEFT)
            fresh = {k: num(k) for k in (a, b)}
            self.play(*[bars[k].animate.become(bar(k)) for k in (a, b)],
                      *[FadeOut(nums[k]) for k in (a, b)], *[FadeIn(fresh[k]) for k in (a, b)],
                      *([FadeOut(note)] if note else []), FadeIn(new), run_time=.75)
            nums.update(fresh); note = new
            self.wait(.25)
        bt = label("Bradley-Terry MLE then fits all matches", 19, SAGE, "BOLD").move_to([x0, -2.2, 0], aligned_edge=LEFT)
        self.play(FadeIn(bt), run_time=.6)
        self.wait(3)


class Listen(Scene):
    """Grammar scoring: attention pooling over Voxtral frames (12.5 per second), trained on a new random
    test-length prefix every epoch. Frame heights and attention weights are illustrative."""

    def construct(self):
        rng = np.random.default_rng(11)
        n, w, x0, base = 56, .2, -5.5, 1.0
        env = np.abs(np.convolve(rng.normal(0, 1, n + 6), np.ones(4) / 4, mode="same"))[3:n + 3]
        env = .25 + 1.3 * env / env.max()
        frames = VGroup(*[Line([x0 + i * w, base - env[i] / 2, 0], [x0 + i * w, base + env[i] / 2, 0], color=INK, stroke_width=6)
                          for i in range(n)])
        title = label("Voxtral frame states, 12.5 per second", 20, INK3).move_to([-6.75, 3.0, 0], aligned_edge=LEFT)
        self.play(FadeIn(title), Create(frames, lag_ratio=.03), run_time=1.6)

        pool = VGroup(label("attention-weighted average", 19, GOLD), label("mean", 19, INK), label("standard deviation", 19, INK))
        pool.arrange(DOWN, aligned_edge=LEFT, buff=.18).move_to([-3.2, -2.45, 0])
        out = label("linear -> grammar score", 20, SAGE, "BOLD").move_to([3.4, -2.45, 0])
        arrows = VGroup(*[Line(h.get_right() + RIGHT * .15, out.get_left() + LEFT * .15, color=INK3, stroke_width=2) for h in pool])
        where = label("attention: where the grammar evidence is", 18, INK3).move_to([x0 - .1, -1.55, 0], aligned_edge=LEFT)
        attn = epoch = bracket = None
        t = np.arange(n)
        for e, L in enumerate((34, 49, 41), 1):
            br = Line([x0 - .1, base + 1.0, 0], [x0 + (L - 1) * w + .1, base + 1.0, 0], color=GOLD, stroke_width=4)
            seg = label(f"epoch {e}: random test-length prefix, {L / 12.5:.1f} s", 19, GOLD).next_to(br, UP, buff=.15).align_to(br, LEFT)
            peaks = rng.choice(np.arange(3, L - 3), 2, replace=False)
            a = .1 + .25 * rng.random(n) + sum(np.exp(-((t - p) / 2.2) ** 2) for p in peaks)
            a = a / a[:L].max()
            new = VGroup(*[Line([x0 + i * w, base - 1.05, 0], [x0 + i * w, base - 1.05 - .95 * a[i], 0],
                                color=GOLD, stroke_width=6) for i in range(L)])
            self.play(*[FadeOut(m) for m in (epoch, bracket, attn) if m], FadeIn(seg), Create(br),
                      *[frames[i].animate.set_opacity(1 if i < L else .2) for i in range(n)], run_time=.8)
            self.play(Create(new, lag_ratio=.02), run_time=1.1)
            if e == 1:
                self.play(FadeIn(where), FadeIn(pool), *[Create(x) for x in arrows], FadeIn(out), run_time=1.0)
            self.wait(.9)
            epoch, bracket, attn = seg, br, new
        self.wait(2.4)


class Lora(Scene):
    """LORA_for_GPU: W frozen in 4-bit NF4, trainable update B A with rank r = 16 on q, k, v, o of the language
    model. d = 3,072 is an example size for the arithmetic."""

    def construct(self):
        from manim import Rectangle, Square
        d, r, side = 3072, 16, 3.4
        W = Square(side_length=side, color=INK3, stroke_width=2, fill_color=INK3, fill_opacity=.18).move_to([-4.85, -.2, 0])
        grid = VGroup(*[Line(W.get_corner(UL) + RIGHT * k * side / 10, W.get_corner(DL) + RIGHT * k * side / 10,
                             color=INK3, stroke_width=1, stroke_opacity=.35) for k in range(1, 10)])
        wl = label("W  d x d", 20, INK, "BOLD").next_to(W, UP, buff=.22)
        wc = label("frozen, 4-bit NF4", 19, INK3).next_to(W, DOWN, buff=.22)
        self.play(Create(W), FadeIn(grid), FadeIn(wl), FadeIn(wc), run_time=1.3)
        plus = label("+", 36, INK).move_to([-2.65, -.2, 0])
        B = Rectangle(width=.34, height=side, color=GOLD, fill_color=GOLD, fill_opacity=.6).move_to([-1.95, -.2, 0])
        BA = Square(side_length=side, color=GOLD, stroke_width=2, fill_color=GOLD, fill_opacity=.22)
        BA.next_to(B, RIGHT, buff=.3)
        A = Rectangle(width=side, height=.34, color=GOLD, fill_color=GOLD, fill_opacity=.6).next_to(BA, UP, buff=.3)
        bl = label("B  d x 16", 19, GOLD).next_to(B, DOWN, buff=.22)
        al = label("A  16 x d", 19, GOLD).next_to(A, UP, buff=.18)
        self.play(FadeIn(plus), FadeIn(B, shift=RIGHT * .3), FadeIn(bl), run_time=.8)
        self.play(FadeIn(A, shift=DOWN * .3), FadeIn(al), run_time=.8)
        bal = label("B A, rank 16", 19, GOLD).next_to(BA, DOWN, buff=.22)
        self.play(Create(BA), FadeIn(bal), run_time=1.2)
        rows = VGroup(
            label(f"example d = {d:,}", 18, INK3),
            label(f"frozen   {d * d:>9,}", 19, INK),
            label(f"trained  {2 * d * r:>9,}", 19, GOLD, "BOLD"),
            label(f"share    {2 * d * r / (d * d):>9.2%}", 19, SAGE, "BOLD"),
            label("on q, k, v and o", 18, INK3),
        ).arrange(DOWN, aligned_edge=LEFT, buff=.22).move_to([5.45, -.2, 0])
        for row in rows:
            self.play(FadeIn(row, shift=LEFT * .2), run_time=.4)
        self.wait(3)


class Prune(Scene):
    """Self-pruning: three lambdas from REPORT.md. Gates start at sigmoid(2.0) = 0.88. Sparsity reached 100% by
    epoch 40 and 20, and 99.99% by epoch 10; test accuracy 93.08%, 91.93%, 84.06%. Per-gate timing is illustrative."""

    def construct(self):
        from manim import Square
        rng = np.random.default_rng(5)
        runs = [("0.01", 40, "100%", "93.08%"), ("0.03", 20, "100%", "91.93%"), ("0.10", 10, "99.99%", "84.06%")]
        k, size = 14, .2
        epoch = ValueTracker(0)
        panels = VGroup()
        for p, (lam, done, sp, acc) in enumerate(runs):
            cx = -4.6 + p * 4.6
            drop = rng.uniform(.25, .95, k * k) * done          # epoch at which each gate falls under 0.01
            cells = VGroup()
            for i in range(k * k):
                sq = Square(side_length=size * .8, stroke_width=1, stroke_color=INK3, stroke_opacity=.5,
                            fill_color=INK, fill_opacity=.88)
                sq.move_to([cx - (k - 1) * size / 2 + (i % k) * size, 2.0 - (i // k) * size, 0])
                sq.add_updater(lambda m, t0=drop[i]: m.set_fill(opacity=.85 / (1 + np.exp((epoch.get_value() - t0) * 1.1)) + .02))
                cells.add(sq)
            panels.add(VGroup(label(f"lambda = {lam}", 20, INK, "BOLD").move_to([cx, 2.9, 0]), cells))
        note = label("classifier-head gates, g = sigmoid(s), starting at 0.88", 18, INK3).to_edge(DOWN, buff=.3)
        ep = always_redraw(lambda: label(f"epoch {int(epoch.get_value()):>3} of 100", 20, GOLD, "BOLD").move_to([0, -.95, 0]))
        self.play(FadeIn(panels), FadeIn(note), FadeIn(ep), run_time=1.2)
        self.play(epoch.animate.set_value(45), run_time=6, rate_func=linear)
        res = VGroup(*[VGroup(label(f"{sp} pruned by epoch {done}", 18, SAGE), label(f"test accuracy {acc}", 20, INK, "BOLD"))
                       .arrange(DOWN, buff=.12).move_to([-4.6 + p * 4.6, -1.85, 0]) for p, (lam, done, sp, acc) in enumerate(runs)])
        self.play(FadeIn(res, lag_ratio=.3), epoch.animate.set_value(100), run_time=2.2, rate_func=linear)
        self.wait(3.2)


class Judge(Scene):
    """CollegeBot evaluation: the 8B writer is graded by a separate 70B judge, and the harness runs at temperature 0.0.
    Refusal accuracy per round is the README table; rounds 3 and 5 ran the same setup (0.974 vs 0.872)."""

    def construct(self):
        from manim import Arrow, SurroundingRectangle
        writer = label("writer  llama-3.1-8b-instant", 19, INK)
        judge = label("judge  llama-3.3-70b-versatile", 19, SAGE, "BOLD")
        temp = label("temperature 0.0", 19, SAGE)
        writer.move_to([-6.75, 1.9, 0], aligned_edge=LEFT)
        judge.move_to([-6.75, .1, 0], aligned_edge=LEFT)
        temp.next_to(judge, DOWN, buff=.15).align_to(judge, LEFT)
        boxes = VGroup(SurroundingRectangle(writer, color=INK3, buff=.18, stroke_width=2),
                       SurroundingRectangle(VGroup(judge, temp), color=SAGE, buff=.18, stroke_width=2))
        arrow = Arrow(boxes[0].get_bottom(), boxes[1].get_top(), color=INK3, buff=.08, stroke_width=3)
        own = label("not the writer grading itself", 18, ROSE).next_to(boxes[1], DOWN, buff=.3).align_to(boxes[1], LEFT)
        strike = Line(own.get_left(), own.get_right(), color=ROSE, stroke_width=2)
        self.play(FadeIn(writer), Create(boxes[0]), run_time=.8)
        self.play(Create(arrow), FadeIn(judge), FadeIn(temp), Create(boxes[1]), run_time=1.0)
        self.play(FadeIn(own), run_time=.5)
        self.wait(.6)

        acc = [.923, .974, .974, .872, .872]
        ax = Axes(x_range=[.5, 5.5, 1], y_range=[.85, 1.0, .05], x_length=5.6, y_length=4.2, tips=False,
                  axis_config={"color": INK3, "stroke_width": 2}).move_to([3.7, -.25, 0])
        yt = VGroup(*[label(f"{v:.2f}", 17).next_to(ax.c2p(.5, v), LEFT, buff=.15) for v in (.85, .90, .95, 1.0)])
        xt = VGroup(*[label(f"{r}", 16).next_to(ax.c2p(r, .85), DOWN, buff=.15) for r in range(1, 6)],
                    label("evaluation round", 16).next_to(ax, DOWN, buff=.5))
        head = label("refusal accuracy per round", 19, INK).next_to(ax, UP, buff=.35).align_to(ax, LEFT)
        target = DashedLine(ax.c2p(.5, .95), ax.c2p(5.5, .95), color=INK3, dash_length=.1)
        tl = label("target 0.95", 16).next_to(ax.c2p(5.5, .95), UP, buff=.08).align_to(ax.c2p(5.5, .95), RIGHT)
        self.play(Create(ax), FadeIn(yt), FadeIn(xt), FadeIn(head), Create(target), FadeIn(tl), run_time=1.1)
        dots = VGroup()
        for r, v in enumerate(acc, 1):
            d = Dot(ax.c2p(r, v), radius=.09, color=GOLD if r in (3, 5) else INK)
            dots.add(d)
            self.play(FadeIn(d, scale=.5), FadeIn(label(f"{v:.3f}", 16, INK).next_to(d, UP, buff=.1)), run_time=.4)
        gap = Line(ax.c2p(4.6, .974), ax.c2p(4.6, .872), color=GOLD, stroke_width=4)
        ticks = VGroup(Line(ax.c2p(4.5, .974), ax.c2p(4.7, .974), color=GOLD, stroke_width=4),
                       Line(ax.c2p(4.5, .872), ax.c2p(4.7, .872), color=GOLD, stroke_width=4))
        link = DashedLine(ax.c2p(3, .974), ax.c2p(4.5, .974), color=GOLD, dash_length=.08, stroke_width=2)
        same = label("rounds 3 and 5: same setup", 18, GOLD, "BOLD").next_to(own, DOWN, buff=.45).align_to(own, LEFT)
        noise = label("noise at temperature 0.05: about 0.10", 18, GOLD).next_to(same, DOWN, buff=.1).align_to(same, LEFT)
        self.play(Create(link), Create(gap), Create(ticks), FadeIn(same), run_time=1.0)
        self.play(FadeIn(noise), run_time=.6)
        fix = label("so the harness now runs at 0.0", 18, SAGE, "BOLD").next_to(noise, DOWN, buff=.3).align_to(own, LEFT)
        self.play(Create(strike), FadeIn(fix), run_time=.8)
        self.wait(3)


class Chain(Scene):
    """CollegeBot follow-up turn: the legacy chain rewrites the question with an extra LLM call before retrieval
    (two sequential requests) and shows the answer in one block; the plain pipeline adds the previous question to the
    search and streams one call. Durations are illustrative."""

    def construct(self):
        from manim import Rectangle
        x0, unit, y1, y2 = -1.5, .6, 1.15, -1.05
        X = lambda v: x0 + v * unit
        def bar(t0, t1, y, colour, text, fill=.85, size=15):
            r = Rectangle(width=(t1 - t0) * unit, height=.5, stroke_width=0, fill_color=colour, fill_opacity=fill)
            r.move_to([X((t0 + t1) / 2), y, 0])
            return VGroup(r, label(text, size, "#000000", "BOLD").move_to(r)) if text else r
        n1 = VGroup(label("ConversationalRetrievalChain", 19, ROSE, "BOLD"), label("2 LLM requests per turn", 17, INK3),
                    label("rewrites the question first", 17, INK3))
        n2 = VGroup(label("retrieve, prompt, stream", 19, SAGE, "BOLD"), label("1 LLM request per turn", 17, INK3),
                    label("search: previous + new question", 17, INK3))
        for g, y in ((n1, y1), (n2, y2)):
            g.arrange(DOWN, aligned_edge=LEFT, buff=.1).move_to([-6.8, y, 0], aligned_edge=LEFT)
        q = label('a follow-up arrives: "and the hostel fee?"', 19, INK).move_to([-6.8, 3.0, 0], aligned_edge=LEFT)
        axis = Line([X(0), -2.3, 0], [X(14), -2.3, 0], color=INK3, stroke_width=2)
        al = label("time", 16).next_to(axis, DOWN, buff=.12).align_to(axis, RIGHT)
        self.play(FadeIn(q), FadeIn(n1), FadeIn(n2), Create(axis), FadeIn(al), run_time=1.1)

        t = ValueTracker(0)
        cursor = always_redraw(lambda: Line([X(t.get_value()), 2.1, 0], [X(t.get_value()), -2.3, 0], color=GOLD,
                                            stroke_width=2, stroke_opacity=.6))
        # the streamed answer fills in as it is generated
        grow = always_redraw(lambda: Rectangle(width=max(min(t.get_value(), 9.5) - 1.5, .001) * unit, height=.5, stroke_width=0,
                                               fill_color=GOLD, fill_opacity=.85 if t.get_value() > 1.5 else 0)
                             .move_to([X(1.5), y2, 0], aligned_edge=LEFT))
        self.add(cursor, grow)
        rewrite, s1 = bar(0, 4, y1, ROSE, "LLM: rewrite"), bar(4, 5.5, y1, INK3, "search", size=14)
        s2 = bar(0, 1.5, y2, INK3, "search", size=14)
        wait = Rectangle(width=8 * unit, height=.5, stroke_color=ROSE, stroke_width=2, fill_opacity=0).move_to([X(9.5), y1, 0])
        answer1 = bar(5.5, 13.5, y1, ROSE, "LLM: answer")
        answer2 = label("LLM: answer, streamed", 15, "#000000", "BOLD").move_to([X(5.5), y2, 0])
        first = VGroup(Line([X(1.5), y2 - .3, 0], [X(1.5), y2 - .55, 0], color=SAGE, stroke_width=3),
                       label("first words on screen", 16, SAGE).move_to([X(1.5), y2 - .75, 0], aligned_edge=LEFT))
        self.play(t.animate.set_value(1.5), FadeIn(rewrite), FadeIn(s2), run_time=1.0, rate_func=linear)
        self.play(FadeIn(first), FadeIn(answer2), t.animate.set_value(4), run_time=1.4, rate_func=linear)
        self.play(FadeIn(s1), t.animate.set_value(5.5), run_time=.8, rate_func=linear)
        self.play(Create(wait), t.animate.set_value(13.5), run_time=4.2, rate_func=linear)
        done = label("whole answer at once", 16, ROSE).move_to([X(13.5), y1 - .55, 0], aligned_edge=RIGHT)
        self.play(FadeIn(answer1), FadeIn(done), run_time=.5)
        note = label("Groq free tier: 6,000 tokens per minute, shared by every visitor", 16, INK3).move_to([-6.8, -3.05, 0], aligned_edge=LEFT)
        self.play(FadeIn(note), run_time=.5)
        self.wait(3)


class Retrieval(Scene):
    """CollegeBot Fig. 1: share of test questions whose answer fact reaches the context, and the latency each setup
    adds. Every number is from the README's retrieval table."""

    def construct(self):
        from manim import Rectangle
        rows = [("Dense MMR, k = 6", 77.1, 0, "none"), ("BM25 only, top 8", 80.0, 0, "none"),
                ("Dense + reranker, top 8", 88.6, 2.0, "+2.0 s"), ("Hybrid dense + BM25, top 8", 88.6, 0, "none"),
                ("Hybrid + reranker, top 8", 85.7, 1.4, "+1.4 s"), ("Hybrid, top 16", 91.4, 0, "none")]
        bx, span, lx = -2.55, 5.0, 4.35                    # bar start, width of 100%, latency column
        y = lambda i: 1.9 - i * .8
        h1 = label("fact reaches the context", 18, INK3).move_to([bx, 2.85, 0], aligned_edge=LEFT)
        h2 = label("added latency", 18, INK3).move_to([lx, 2.85, 0], aligned_edge=LEFT)
        names = VGroup(*[label(r[0], 18, INK).move_to([-6.8, y(i), 0], aligned_edge=LEFT) for i, r in enumerate(rows)])
        base = Line([bx, 2.4, 0], [bx, y(5) - .4, 0], color=INK3, stroke_width=2)
        self.play(FadeIn(h1), FadeIn(h2), FadeIn(names, lag_ratio=.1), Create(base), run_time=1.2)

        bars, vals = VGroup(), VGroup()
        for i, (name, v, lat, ltxt) in enumerate(rows):
            b = Rectangle(width=span * v / 100, height=.42, stroke_width=0, fill_color=INK, fill_opacity=.85)
            b.move_to([bx, y(i), 0], aligned_edge=LEFT)
            bars.add(b)
            vals.add(label(f"{v:.1f}%", 18, INK).next_to(b, RIGHT, buff=.15))
        from manim import GrowFromEdge
        self.play(*[GrowFromEdge(b, LEFT) for b in bars], *[FadeIn(v) for v in vals], lag_ratio=.15, run_time=2.2)
        lats = VGroup()
        for i, (name, v, lat, ltxt) in enumerate(rows):
            if lat:
                r = Rectangle(width=lat * .75, height=.42, stroke_width=0, fill_color=ROSE, fill_opacity=.85)
                r.move_to([lx, y(i), 0], aligned_edge=LEFT)
                lats.add(VGroup(r, label(ltxt, 18, ROSE).next_to(r, RIGHT, buff=.12)))
            else:
                lats.add(label(ltxt, 18, INK3).move_to([lx, y(i), 0], aligned_edge=LEFT))
        self.play(*[FadeIn(l, shift=RIGHT * .2) for l in lats], run_time=1.0)
        self.wait(.6)

        tie = VGroup(Line(bars[2].get_right() + RIGHT * .95, bars[3].get_right() + RIGHT * .95, color=GOLD, stroke_width=4))
        tl = label("same 88.6%", 18, GOLD, "BOLD").next_to(tie, RIGHT, buff=.15)
        self.play(Create(tie), FadeIn(tl), *[b.animate.set_fill(GOLD) for b in bars[2:4]], run_time=.9)
        self.wait(.8)
        worse = label("reranker on top made it worse", 17, ROSE).move_to([-6.8, -2.95, 0], aligned_edge=LEFT)
        self.play(bars[4].animate.set_fill(ROSE, opacity=.7), FadeIn(worse), run_time=.8)
        tokens = label("top 16: +2.8 points for twice the context tokens", 17, INK3).next_to(worse, DOWN, buff=.1).align_to(worse, LEFT)
        self.play(bars[5].animate.set_fill(INK3, opacity=.6), FadeIn(tokens), run_time=.8)
        ship = label("shipped", 18, SAGE, "BOLD").next_to(lats[3], RIGHT, buff=.3)
        self.play(bars[3].animate.set_fill(SAGE), names[3].animate.set_color(SAGE), vals[3].animate.set_color(SAGE),
                  FadeIn(ship), FadeOut(tie), FadeOut(tl), bars[2].animate.set_fill(INK), run_time=1.0)
        self.wait(3)
