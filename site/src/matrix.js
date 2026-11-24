(() => {
  const chamber = document.querySelector(".chamber");
  const canvas = chamber.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const fallback = chamber.querySelector(".glyph-fallback");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const face = '700 240px "Codex Mono"';
  const names = { a: "lowercase a", g: "lowercase g", 0: "zero" };
  const tones = [85, 109, 133, 157, 183, 210, 233, 255];
  const grays = Array.from({ length: 256 }, (_, n) => "rgb(" + n + "," + n + "," + n + ")");
  let glyph = "a";
  let width, height, columns, pitch, line, layouts, density;
  let shown, from, to, printOrder, start, selectedAt, paintedAt, entrance;
  let frame = null;

  function sample(letter) {
    const mask = document.createElement("canvas");
    const pen = mask.getContext("2d", { willReadFrequently: true });
    pen.font = face;
    const bounds = pen.measureText(letter);
    mask.width = Math.ceil(bounds.actualBoundingBoxLeft + bounds.actualBoundingBoxRight) + 4;
    mask.height = Math.ceil(bounds.actualBoundingBoxAscent + bounds.actualBoundingBoxDescent) + 4;
    pen.font = face;
    pen.fillText(letter, bounds.actualBoundingBoxLeft + 2, bounds.actualBoundingBoxAscent + 2);
    const ink = pen.getImageData(0, 0, mask.width, mask.height).data;

    const scale = Math.min(.72 * height / mask.height, .57 * width / mask.width);
    const depthX = .087 * width;
    const depthY = -.076 * height;
    const centerX = .5 * width - depthX / 2;
    const centerY = .5 * height - depthY / 2;
    const shearX = .23, shearY = .12;
    const determinant = 1 - shearX * shearY;
    function inside(x, y) {
      const u = (x - centerX) / scale;
      const v = (y - centerY) / scale;
      const mx = Math.floor((u + shearX * v) / determinant + mask.width / 2);
      const my = Math.floor((v + shearY * u) / determinant + mask.height / 2);
      return mx >= 0 && mx < mask.width && my >= 0 && my < mask.height && ink[(my * mask.width + mx) * 4 + 3] > 100;
    }

    const cells = [];
    for (let row = 0; row * line < height; row++) {
      for (let col = 0; col < columns; col++) {
        const x = (col + .5) * pitch;
        const y = (row + .5) * line;
        let depth = 0;
        while (depth <= 12 && !inside(x - depth * depthX / 12, y - depth * depthY / 12)) depth++;
        if (depth > 12) continue;
        const seed = (col * 17 + row * 31 + col * row) % 97;
        const edge = !depth && (!inside(x - pitch, y) || !inside(x, y - line));
        const band = Math.sin(row * .34 + col * .11);
        const color = depth ? Math.min(3, Math.floor((12 - depth) / 4) + (row % 4 === 0 ? 1 : 0))
          : edge ? 7 : band > .5 ? 6 : band < -.52 ? 4 : 5;
        const alphabet = depth ? "+/1x:=" : edge ? "8@%0" : "a0@%#x8";
        cells.push({ x, y, char: alphabet[seed % alphabet.length], tone: tones[color], alpha: 1, delay: col / columns * .32 });
      }
    }
    const lanes = Math.max(1, columns - 12);
    const bandCount = Math.ceil(cells.length / lanes);
    cells.forEach((cell, i) => {
      cell.fromX = (i % lanes + 6) * pitch;
      cell.fromY = height * (.49 + .12 * Math.sin(cell.fromX / width * 8))
        + (Math.floor(i / lanes) - bandCount / 2) * line * .75;
    });
    return cells;
  }

  function spatialSlots(points, count, axis) {
    if (count === 1) return points;
    if (points.length === 1) {
      const [point] = points;
      return [point, ...Array(count - 1).fill({ ...point, alpha: 0 })];
    }
    const next = axis === "y" ? "x" : "y";
    points.sort((a, b) => a[axis] - b[axis] || a[next] - b[next]);
    const mid = Math.ceil(points.length / 2), half = Math.ceil(count / 2);
    return spatialSlots(points.slice(0, mid), half, next)
      .concat(spatialSlots(points.slice(mid), count - half, next));
  }

  function typeset() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return false;
    width = w;
    height = h;
    density = 0;
    columns = Math.max(1, Math.round(width / (width < 400 ? 4.3 : 5.25)));
    pitch = width / columns;
    line = pitch * 1.42;
    const letters = Object.keys(names);
    const samples = letters.map(sample);
    const chars = new Set(samples.flat().map(cell => cell.char));
    layouts = Object.fromEntries(letters.map(letter => [letter, []]));
    for (const char of chars) {
      const groups = samples.map(cells => cells.filter(cell => cell.char === char));
      const count = Math.max(...groups.map(group => group.length));
      groups.forEach((points, i) => {
        if (!points.length) points.push({ x: width / 2, y: height / 2, fromX: width / 2,
          fromY: height / 2, delay: 0, char, tone: tones[0], alpha: 0 });
        layouts[letters[i]].push(...spatialSlots(points, count, "y"));
      });
    }
    return true;
  }

  function draw() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (dpr !== density) {
      density = dpr;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.font = '700 ' + (pitch * 1.56) + 'px "Codex Mono"';
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
    }
    ctx.clearRect(0, 0, width, height);
    for (const i of printOrder) {
      const mark = shown[i];
      if (!mark.alpha) continue;
      ctx.globalAlpha = mark.alpha;
      ctx.fillStyle = grays[Math.round(mark.tone)];
      ctx.fillText(mark.char, mark.x, mark.y);
    }
  }

  function watchDensity() {
    matchMedia("(resolution: " + (window.devicePixelRatio || 1) + "dppx)").addEventListener("change", () => {
      watchDensity();
      draw();
    }, { once: true });
  }

  function orderByRow() {
    printOrder = to.map((_, i) => i).sort((i, j) => to[i].y - to[j].y || to[i].x - to[j].x);
  }

  function settle() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    from = null;
    to = layouts[glyph];
    orderByRow();
    shown = to.map(cell => ({ ...cell, vx: 0, vy: 0 }));
    draw();
  }

  function schedule() {
    if (frame === null) frame = requestAnimationFrame(tick);
  }

  function tick(now) {
    frame = null;
    if (to !== layouts[glyph]) {
      start = from ? Math.max(paintedAt, selectedAt - 1000 / 30) : selectedAt;
      from = shown;
      shown = from.map(mark => ({ ...mark }));
      to = layouts[glyph];
      entrance = false;
    }
    if (!from) return;
    const duration = entrance ? 1700 : 850;
    const progress = (now - start) / duration;
    if (progress >= 1) return settle();
    for (let i = 0; i < shown.length; i++) {
      const a = from[i], b = to[i], p = shown[i];
      const delay = entrance ? b.delay : 0;
      const t = Math.max(0, (progress - delay) / (1 - delay));
      const span = duration * (1 - delay);
      const mix = t * t * (3 - 2 * t);
      const carry = t * (1 - t) * (1 - t) * span;
      const slope = 6 * t * (1 - t) / span;
      const momentum = (1 - t) * (1 - 3 * t);
      p.x = a.x + (b.x - a.x) * mix + a.vx * carry;
      p.y = a.y + (b.y - a.y) * mix + a.vy * carry;
      p.vx = (b.x - a.x) * slope + a.vx * momentum;
      p.vy = (b.y - a.y) * slope + a.vy * momentum;
      p.tone = a.tone + (b.tone - a.tone) * mix;
      p.alpha = a.alpha + (b.alpha - a.alpha) * mix;
    }
    paintedAt = now;
    draw();
    schedule();
  }

  function replay() {
    if (motion.matches || document.hidden) return settle();
    to = layouts[glyph];
    orderByRow();
    from = to.map(cell => ({ ...cell, x: cell.fromX, y: cell.fromY, vx: 0, vy: 0 }));
    shown = from.map(mark => ({ ...mark }));
    entrance = true;
    start = performance.now();
    paintedAt = start;
    draw();
    schedule();
  }

  async function mount() {
    const loaded = await document.fonts.load(face, "ag0");
    if (!loaded.length) return;
    if (!typeset()) {
      requestedFace = false;
      return;
    }
    replay();
    watchDensity();
    fallback.hidden = true;
    chamber.setAttribute("aria-label", "An enlarged lowercase a, composed of tiny monospaced characters.");
    document.querySelector(".glyph-choices").hidden = false;
    document.querySelector(".replay").hidden = false;
    for (const button of document.querySelectorAll("[data-glyph]")) {
      button.addEventListener("click", () => {
        if (glyph === button.dataset.glyph) return;
        glyph = button.dataset.glyph;
        for (const choice of document.querySelectorAll("[data-glyph]")) {
          choice.setAttribute("aria-pressed", String(choice === button));
        }
        chamber.setAttribute("aria-label", "An enlarged " + names[glyph] + ", composed of tiny monospaced characters.");
        document.querySelector(".reading-size b").textContent = glyph;
        chamber.querySelector(".codepoint").textContent = "U+" + glyph.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
        if (motion.matches || document.hidden) return settle();
        selectedAt = performance.now();
        schedule();
      });
    }
    document.querySelector(".replay").addEventListener("click", replay);
    motion.addEventListener("change", settle);
    document.addEventListener("visibilitychange", () => { if (document.hidden) settle(); });
  }

  if (!ctx || !document.fonts || !window.ResizeObserver) return;
  let requestedFace = false;
  new ResizeObserver(([entry]) => {
    if (!entry.contentRect.width || !entry.contentRect.height) return;
    if (!requestedFace) {
      requestedFace = true;
      mount().catch(() => { fallback.hidden = false; });
    } else if (layouts && (width !== canvas.clientWidth || height !== canvas.clientHeight)) {
      if (typeset()) settle();
    }
  }).observe(canvas);
})();
