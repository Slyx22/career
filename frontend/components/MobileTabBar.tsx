"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef } from "react";
import { BadgeIcon, HomeIcon, ScanIcon } from "@/components/Icons";

const TABS = [
  { href: "/", label: "Home", Icon: HomeIcon, match: (p: string) => p === "/" },
  { href: "/analyze", label: "Check my CV", Icon: ScanIcon, match: (p: string) => p.startsWith("/analyze") || p.startsWith("/results") },
  {
    href: "/dashboard",
    label: "Certificates",
    Icon: BadgeIcon,
    match: (p: string) => p.startsWith("/dashboard") || p.startsWith("/certificate") || p.startsWith("/verify"),
  },
];

// Spring tuning. Slightly under-damped so the lens overshoots a touch and
// settles, which is what gives iOS liquid glass its "water" feel.
const STIFFNESS = 380;
const DAMPING = 30;
const PRESS_STIFFNESS = 520;
const PRESS_DAMPING = 26;

// Text/icon colours we blend between as the lens passes over a tab.
const IDLE = [75, 84, 104]; // slate
const ACTIVE = [86, 70, 184]; // jacaranda-dark

function mix(a: number[], b: number[], t: number) {
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(",")})`;
}

/**
 * iOS-style floating liquid-glass tab bar, phones and small tablets only.
 *
 * The selected "lens" is driven by a small spring simulation (written
 * straight to the DOM each frame, no React re-renders), so it:
 *  - glides between tabs and stretches with its speed, like a drop of water
 *  - lifts and grows under your finger, and follows it when you drag
 *  - snaps to the nearest tab when you let go
 * The whole bar also swells slightly while pressed.
 */
export function MobileTabBar() {
  const pathname = usePathname() || "/";
  const router = useRouter();
  // -1 on pages without a tab (Privacy, Terms...): the lens hides there.
  const matched = TABS.findIndex((t) => t.match(pathname));
  const activeIndex = Math.max(0, matched);
  const noTab = matched === -1;
  // Always the CURRENT page. Listeners set up once (resize) read this, not a
  // value captured when the bar first mounted: phones fire "resize" on every
  // scroll as the address bar slides, which used to snap the lens back to
  // whichever page the site was first opened on.
  const activeRef = useRef(activeIndex);
  activeRef.current = activeIndex;
  const hiddenRef = useRef(noTab);
  hiddenRef.current = noTab;

  const barRef = useRef<HTMLDivElement>(null);
  const lensRef = useRef<HTMLDivElement>(null);
  const tabRefs = useRef<(HTMLAnchorElement | null)[]>([]);

  // Physics state lives in a ref so animation never triggers a render.
  const s = useRef({
    x: 0, // lens left edge, px within the bar
    v: 0, // velocity, px/s
    target: 0,
    w: 0, // lens width
    press: 0, // 0 = resting, 1 = finger down (lifts lens, swells bar)
    pv: 0,
    pressTarget: 0,
    raf: 0,
    last: 0,
    ready: false,
    reduced: false,
    // drag tracking
    pointerId: -1,
    startX: 0,
    startY: 0,
    gaveUp: false, // the gesture turned out to be a vertical scroll
    grabOffset: 0,
    dragged: false,
  });

  const tabBox = useCallback((i: number) => {
    const bar = barRef.current;
    const tab = tabRefs.current[i];
    if (!bar || !tab) return null;
    const b = bar.getBoundingClientRect();
    const r = tab.getBoundingClientRect();
    return { left: r.left - b.left, width: r.width };
  }, []);

  const paint = useCallback(() => {
    const st = s.current;
    const lens = lensRef.current;
    const bar = barRef.current;
    if (!lens || !bar) return;

    // Stretch along the direction of travel and squash vertically — the
    // faster it moves, the more it flows. Pressing also makes it bigger.
    const speed = Math.min(Math.abs(st.v) / 2600, 1);
    const sx = 1 + speed * 0.32 + st.press * 0.12;
    const sy = 1 - speed * 0.16 + st.press * 0.1;
    lens.style.width = `${st.w}px`;
    lens.style.transform = `translate3d(${st.x}px,0,0) scale(${sx},${sy})`;
    lens.style.setProperty("--lift", String(st.press));
    lens.style.opacity = hiddenRef.current ? "0" : "1";

    bar.style.transform = `scale(${1 + st.press * 0.035})`;

    // Fade the tab colours with how much the lens covers each tab.
    const centre = st.x + st.w / 2;
    tabRefs.current.forEach((tab, i) => {
      const box = tabBox(i);
      if (!tab || !box) return;
      const d = Math.abs(centre - (box.left + box.width / 2)) / box.width;
      tab.style.color = hiddenRef.current ? mix(IDLE, ACTIVE, 0) : mix(IDLE, ACTIVE, Math.max(0, 1 - d * 1.4));
    });
  }, [tabBox]);

  const step = useCallback(
    (now: number) => {
      const st = s.current;
      const dt = Math.min((now - st.last) / 1000, 1 / 30);
      st.last = now;

      if (st.pointerId === -1 || !st.dragged) {
        // Spring towards the target tab.
        const a = -STIFFNESS * (st.x - st.target) - DAMPING * st.v;
        st.v += a * dt;
        st.x += st.v * dt;
      }
      const pa = -PRESS_STIFFNESS * (st.press - st.pressTarget) - PRESS_DAMPING * st.pv;
      st.pv += pa * dt;
      st.press += st.pv * dt;

      paint();

      const settled =
        Math.abs(st.x - st.target) < 0.3 &&
        Math.abs(st.v) < 4 &&
        Math.abs(st.press - st.pressTarget) < 0.002 &&
        Math.abs(st.pv) < 0.01 &&
        st.pointerId === -1;
      if (settled) {
        st.x = st.target;
        st.v = 0;
        st.press = st.pressTarget;
        st.pv = 0;
        paint();
        st.raf = 0;
        return;
      }
      st.raf = requestAnimationFrame(step);
    },
    [paint]
  );

  const kick = useCallback(() => {
    const st = s.current;
    if (st.reduced) {
      st.x = st.target;
      st.v = 0;
      st.press = 0;
      paint();
      return;
    }
    if (!st.raf) {
      st.last = performance.now();
      st.raf = requestAnimationFrame(step);
    }
  }, [paint, step]);

  const moveTo = useCallback(
    (i: number, instant = false) => {
      const box = tabBox(i);
      if (!box) return;
      const st = s.current;
      st.target = box.left;
      st.w = box.width;
      if (instant || !st.ready) {
        st.x = box.left;
        st.v = 0;
        st.ready = true;
        paint();
      } else {
        kick();
      }
    },
    [kick, paint, tabBox]
  );

  // Follow the current page.
  useEffect(() => {
    moveTo(activeIndex);
    if (noTab) paint();
  }, [activeIndex, noTab, moveTo, paint]);

  // First layout, resizes, and reduced-motion preference.
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    s.current.reduced = mq.matches;
    const onMq = () => (s.current.reduced = mq.matches);
    mq.addEventListener?.("change", onMq);
    moveTo(activeRef.current, true);
    const onResize = () => {
      // Ignore resizes during a drag, and always snap to the page we're on now.
      if (s.current.pointerId !== -1) return;
      moveTo(activeRef.current, true);
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      mq.removeEventListener?.("change", onMq);
      cancelAnimationFrame(s.current.raf);
      s.current.raf = 0;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const nearestTab = (x: number) => {
    let best = 0;
    let bestD = Infinity;
    TABS.forEach((_, i) => {
      const box = tabBox(i);
      if (!box) return;
      const d = Math.abs(x - (box.left + box.width / 2));
      if (d < bestD) {
        bestD = d;
        best = i;
      }
    });
    return best;
  };

  const onPointerDown = (e: React.PointerEvent) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    const st = s.current;
    const bar = barRef.current;
    if (!bar) return;
    const localX = e.clientX - bar.getBoundingClientRect().left;
    st.pointerId = e.pointerId;
    st.startX = e.clientX;
    st.startY = e.clientY;
    st.dragged = false;
    st.gaveUp = false;
    // If you grab the lens itself you drag it from where you touched it;
    // otherwise it will centre itself under your finger once you move.
    const onLens = localX >= st.x && localX <= st.x + st.w;
    st.grabOffset = onLens ? localX - st.x : st.w / 2;
    st.pressTarget = 1;
    kick();
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const st = s.current;
    const bar = barRef.current;
    if (e.pointerId !== st.pointerId || !bar) return;
    if (!st.dragged) {
      const dx = Math.abs(e.clientX - st.startX);
      const dy = Math.abs(e.clientY - st.startY);
      // Mostly up or down: it's a scroll. Let go and never switch tabs.
      if (dy > 8 && dy > dx) {
        st.gaveUp = true;
        st.pointerId = -1;
        st.pressTarget = 0;
        st.target = tabBox(activeIndex)?.left ?? st.target;
        kick();
        return;
      }
      // Only a clear sideways swipe starts dragging the lens.
      if (dx > 14 && dx > dy * 1.5) {
        st.dragged = true;
        bar.setPointerCapture?.(e.pointerId);
      }
    }
    if (!st.dragged) return;
    const b = bar.getBoundingClientRect();
    const first = tabBox(0);
    const lastBox = tabBox(TABS.length - 1);
    if (!first || !lastBox) return;
    const min = first.left;
    const max = lastBox.left + lastBox.width - st.w;
    let x = e.clientX - b.left - st.grabOffset;
    // Rubber-band past the ends, like iOS.
    if (x < min) x = min - Math.sqrt(min - x) * 2;
    if (x > max) x = max + Math.sqrt(x - max) * 2;
    const now = performance.now();
    const dt = Math.max((now - st.last) / 1000, 1 / 120);
    st.v = st.v * 0.6 + ((x - st.x) / dt) * 0.4;
    st.x = x;
    st.last = now;
    kick();
  };

  const release = (e: React.PointerEvent, cancelled: boolean) => {
    const st = s.current;
    if (e.pointerId !== st.pointerId) return;
    st.pointerId = -1;
    st.pressTarget = 0;
    if (st.dragged && !cancelled) {
      // Change tab only if the lens was actually carried over another tab.
      const i = nearestTab(st.x + st.w / 2);
      const travelled = Math.abs(e.clientX - st.startX);
      if (i !== activeIndex && travelled > 24) {
        st.target = tabBox(i)?.left ?? st.target;
        router.push(TABS[i].href);
      } else {
        st.target = tabBox(activeIndex)?.left ?? st.target;
      }
    } else if (cancelled) {
      st.target = tabBox(activeIndex)?.left ?? st.target;
    }
    kick();
  };

  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 z-50 flex justify-center px-4 print:hidden md:hidden"
      style={{ bottom: "calc(0.75rem + env(safe-area-inset-bottom, 0px))" }}
    >
      <div
        ref={barRef}
        className="glass liquid-bar relative flex w-full max-w-sm items-stretch gap-1 rounded-full p-1.5"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={(e) => release(e, false)}
        onPointerCancel={(e) => release(e, true)}
      >
        <div ref={lensRef} aria-hidden className="liquid-lens" />
        {TABS.map(({ href, label, Icon }, i) => {
          const active = !noTab && i === activeIndex;
          return (
            <Link
              key={href}
              href={href}
              ref={(el) => {
                tabRefs.current[i] = el;
              }}
              aria-current={active ? "page" : undefined}
              draggable={false}
              onClick={(e) => {
                // A drag already decided on release, and a scroll that began
                // on the bar must never count as a tap.
                if (s.current.dragged || s.current.gaveUp) {
                  e.preventDefault();
                  s.current.dragged = false;
                  s.current.gaveUp = false;
                  return;
                }
                // Tap: start the lens flowing straight away, before the page loads.
                moveTo(i);
              }}
              className="focus-ring relative z-[2] flex min-h-[52px] flex-1 select-none flex-col items-center justify-center gap-0.5 rounded-full text-[11px] font-medium"
              style={{ color: active ? "#5646B8" : "#4B5468", WebkitTouchCallout: "none" }}
            >
              <Icon />
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
