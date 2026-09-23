// Helpers for charts drawn at the size they're shown (never scaled down with a
// viewBox), so text stays readable on every screen.

export const FONT_SIZE = 12;

// Pass as Observable Plot's `style` option.
export const chartStyle = {
  fontSize: `${FONT_SIZE}px`,
  fontFamily: "var(--font-ui)",
  overflow: "visible",
};

// Pixel width of the widest string at the chart font, for sizing label margins.
export function textWidth(strings, size = FONT_SIZE) {
  const ctx = document.createElement("canvas").getContext("2d");
  const family = getComputedStyle(document.body).getPropertyValue("--font-ui") || "sans-serif";
  ctx.font = `${size}px ${family}`;
  let widest = 0;
  for (const s of strings) widest = Math.max(widest, ctx.measureText(String(s)).width);
  return Math.ceil(widest);
}

// Call `draw()` again (debounced) whenever `el` changes width. Returns a function
// that stops watching.
export function redrawOnResize(el, draw, delay = 150) {
  let lastWidth = Math.round(el.clientWidth);
  let timer;
  const observer = new ResizeObserver(([entry]) => {
    const width = Math.round(entry.contentRect.width);
    if (width === lastWidth) return;
    lastWidth = width;
    clearTimeout(timer);
    timer = setTimeout(draw, delay);
  });
  observer.observe(el);
  return () => observer.disconnect();
}
