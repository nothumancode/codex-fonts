(() => {
  const chamber = document.querySelector(".chamber");
  const canvas = chamber.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const fallback = chamber.querySelector(".glyph-fallback");
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const face = '700 240px "Codex Mono"';
  const names = { a: "lowercase a", g: "lowercase g", 0: "zero" };
  const colors = ["#754b32", "#a16138", "#c77b47", "#df8951", "#ef8646", "#ff9954", "#ffb370", "#ffd7a0"];
  let glyph = "a";
  let width, height, pitch, line, cells, frame;

  function typeset() {
    width = canvas.clientWidth;
    height = canvas.clientHeight;
    if (!width || !height) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const mask = document.createElement("canvas");
    const pen = mask.getContext("2d", { willReadFrequently: true });
    pen.font = face;
    const bounds = pen.measureText(glyph);
    mask.width = Math.ceil(bounds.actualBoundingBoxLeft + bounds.actualBoundingBoxRight) + 4;
    mask.height = Math.ceil(bounds.actualBoundingBoxAscent + bounds.actualBoundingBoxDescent) + 4;
    pen.font = face;
    pen.fillText(glyph, bounds.actualBoundingBoxLeft + 2, bounds.actualBoundingBoxAscent + 2);
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

    const columns = Math.round(width / (width < 400 ? 4.3 : 5.25));
    pitch = width / columns;
    line = pitch * 1.42;
    cells = [];
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
        cells.push({ x, y, char: alphabet[seed % alphabet.length], color, delay: col / columns * .32 });
      }
    }
    const lanes = columns - 12;
    const bandCount = Math.ceil(cells.length / lanes);
    cells.forEach((cell, i) => {
      cell.fromX = (i % lanes + 6) * pitch;
      cell.fromY = height * (.49 + .12 * Math.sin(cell.fromX / width * 8))
        + (Math.floor(i / lanes) - bandCount / 2) * line * .75;
    });
  }

  function draw(progress) {
    if (!cells) return;
    ctx.clearRect(0, 0, width, height);
    ctx.font = '700 ' + (pitch * 1.56) + 'px "Codex Mono"';
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (const cell of cells) {
      const t = Math.max(0, Math.min(1, (progress - cell.delay) / (1 - cell.delay)));
      const mix = t * t * (3 - 2 * t);
      ctx.fillStyle = colors[cell.color];
      ctx.fillText(cell.char, cell.fromX + (cell.x - cell.fromX) * mix, cell.fromY + (cell.y - cell.fromY) * mix);
    }
  }

  function settle() {
    cancelAnimationFrame(frame);
    draw(1);
  }

  function compose() {
    cancelAnimationFrame(frame);
    if (motion.matches || document.hidden) return draw(1);
    const start = performance.now();
    function tick(now) {
      const progress = Math.min(1, (now - start) / 1700);
      draw(progress);
      if (progress < 1) frame = requestAnimationFrame(tick);
    }
    frame = requestAnimationFrame(tick);
  }

  async function mount() {
    const loaded = await document.fonts.load(face, "ag0");
    if (!loaded.length) return;
    typeset();
    draw(motion.matches || document.hidden ? 1 : 0);
    fallback.hidden = true;
    chamber.setAttribute("aria-label", "An enlarged lowercase a, composed of tiny monospaced characters.");
    document.querySelector(".glyph-choices").hidden = false;
    document.querySelector(".replay").hidden = false;
    for (const button of document.querySelectorAll("[data-glyph]")) {
      button.addEventListener("click", () => {
        glyph = button.dataset.glyph;
        for (const choice of document.querySelectorAll("[data-glyph]")) {
          choice.setAttribute("aria-pressed", String(choice === button));
        }
        chamber.setAttribute("aria-label", "An enlarged " + names[glyph] + ", composed of tiny monospaced characters.");
        document.querySelector(".reading-size b").textContent = glyph;
        chamber.querySelector(".codepoint").textContent = "U+" + glyph.codePointAt(0).toString(16).toUpperCase().padStart(4, "0");
        typeset();
        compose();
      });
    }
    document.querySelector(".replay").addEventListener("click", compose);
    motion.addEventListener("change", settle);
    document.addEventListener("visibilitychange", () => { if (document.hidden) settle(); });
    compose();
  }

  if (!ctx || !document.fonts || !window.ResizeObserver) return;
  let requestedFace = false;
  new ResizeObserver(([entry]) => {
    if (!entry.contentRect.width) return;
    if (!requestedFace) {
      requestedFace = true;
      mount().catch(() => { fallback.hidden = false; });
    } else if (cells && (width !== canvas.clientWidth || height !== canvas.clientHeight)) {
      typeset();
      settle();
    }
  }).observe(chamber);
})();
