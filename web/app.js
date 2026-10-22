(() => {
  "use strict";

  const STORAGE_KEY = "line-sim-web-v1";
  const MODES = ["manual", "blink", "sequence"];
  const LIMITS = {
    x: [0, 20000],
    y: [0, 20000],
    w: [4, 4000],
    h: [4, 4000],
    period: [100, 10000],
    phase: [0, 100],
  };
  const SEQUENCE_LIMITS = [200, 10000];

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  const el = {
    stage: $("#stage"),
    cards: $$(".card"),
    rects: $$(".rect"),
    chips: $$(".sensor-chip"),
    liveDots: $$(".live-dot"),
    stateValue: $("#stateValue"),
    stateButtons: $$(".state-btn"),
    modeButtons: $$(".seg-btn"),
    colorToggles: $$(".color-toggle"),
    colorButtons: $$(".color-btn"),
    guides: $("#showGuides"),
    playback: $("#playback"),
    playBtn: $("#btnPlay"),
    playLabel: $("#playLabel"),
    sequenceField: $("#sequenceIntervalField"),
    sequenceInput: $("#sequenceInterval"),
    robotBtn: $("#btnRobotMode"),
    resetButtons: $$("#btnReset, #btnResetAdjust"),
    centerBtn: $("#btnCenter"),
    exitRobotBtn: $("#btnExitRobot"),
    liveIndicator: $("#liveIndicator"),
    segIndicator: $(".seg-indicator"),
    surfaceSize: $("#surfaceSize"),
    ruler: $("#stageRuler"),
    stageDock: $("#stageDock"),
    adjuster: $("#adjuster"),
    adjustButtons: $$("[data-adjust]"),
    closeAdjust: $("#btnCloseAdjust"),
    helpDialog: $("#helpDialog"),
    helpButtons: [$("#btnHelp"), $("#btnHelpHero")].filter(Boolean),
    closeHelp: $("#btnCloseHelp"),
  };

  let config = null;
  let currentColors = [false, false, false];
  let selectedIndex = null;
  let saveTimer = 0;
  let resizeTimer = 0;
  let cursorTimer = 0;
  let wakeLock = null;
  let wakeLockPending = false;
  let resizeObserver = null;

  const anim = {
    elapsed: 0,
    sequenceIndex: 0,
    sequenceAccum: 0,
    lastTs: null,
  };

  init();

  function init() {
    config = loadConfig();
    initStateDots();
    bindEvents();
    setupHelp();
    setupAdjuster();
    setupSelection();
    setupDrag();
    applyAllGeometry();
    renderCurrentColors();
    syncControls();
    ensureRectsVisible();
    renderRuler();
    syncSurfaceMeta();
    updateSegIndicator();

    requestAnimationFrame(() => document.body.classList.add("is-ready"));
    requestAnimationFrame(tick);

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => {
        updateSegIndicator();
        renderRuler();
        syncSurfaceMeta();
      });
    }

    if ("ResizeObserver" in window) {
      resizeObserver = new ResizeObserver(() => {
        renderRuler();
        syncSurfaceMeta();
      });
      resizeObserver.observe(el.stage);
    }
  }

  /* ------------------------------------------------------------------ */
  /* configuration                                                       */
  /* ------------------------------------------------------------------ */

  function makeDefaultRects() {
    const stageWidth = Math.max(260, el.stage.clientWidth || window.innerWidth || 800);
    let gap = 60;
    let width = 80;
    if (stageWidth < 3 * width + 2 * gap + 16) {
      gap = 12;
      width = Math.max(40, Math.min(80, Math.floor((stageWidth - 16 - 2 * gap) / 3)));
    }
    const total = 3 * width + 2 * gap;
    const start = Math.max(8, Math.round((stageWidth - total) / 2));
    const periods = [700, 900, 1100];
    const phases = [0, 33, 66];

    return ["L", "C", "R"].map((id, index) => ({
      id,
      x: start + index * (width + gap),
      y: 80,
      w: width,
      h: 40,
      period: periods[index],
      phase: phases[index],
    }));
  }

  function defaultConfig() {
    return {
      mode: "manual",
      running: true,
      showGuides: true,
      sequenceInterval: 800,
      manualColors: [false, true, false],
      rects: makeDefaultRects(),
    };
  }

  function loadConfig() {
    const fallback = defaultConfig();
    let raw = null;

    try {
      raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    } catch {
      raw = null;
    }

    if (!raw || typeof raw !== "object") return fallback;

    const rects = fallback.rects.map((base, index) => {
      const saved = Array.isArray(raw.rects) ? raw.rects[index] : null;
      if (!saved || typeof saved !== "object") return base;
      return {
        ...base,
        x: Math.round(clampNumber(saved.x, LIMITS.x[0], LIMITS.x[1], base.x)),
        y: Math.round(clampNumber(saved.y, LIMITS.y[0], LIMITS.y[1], base.y)),
        w: Math.round(clampNumber(saved.w, LIMITS.w[0], LIMITS.w[1], base.w)),
        h: Math.round(clampNumber(saved.h, LIMITS.h[0], LIMITS.h[1], base.h)),
        period: clampNumber(saved.period, LIMITS.period[0], LIMITS.period[1], base.period),
        phase: clampNumber(saved.phase, LIMITS.phase[0], LIMITS.phase[1], base.phase),
      };
    });

    const manualColors =
      Array.isArray(raw.manualColors) && raw.manualColors.length === 3
        ? raw.manualColors.map(Boolean)
        : fallback.manualColors;

    return {
      mode: MODES.includes(raw.mode) ? raw.mode : fallback.mode,
      running: typeof raw.running === "boolean" ? raw.running : fallback.running,
      showGuides: typeof raw.showGuides === "boolean" ? raw.showGuides : fallback.showGuides,
      sequenceInterval: clampNumber(
        raw.sequenceInterval,
        SEQUENCE_LIMITS[0],
        SEQUENCE_LIMITS[1],
        fallback.sequenceInterval
      ),
      manualColors,
      rects,
    };
  }

  function saveConfigSoon() {
    clearTimeout(saveTimer);
    saveTimer = window.setTimeout(saveConfigNow, 150);
  }

  function saveConfigNow() {
    clearTimeout(saveTimer);
    saveTimer = 0;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    } catch {
      /* localStorage pode estar indisponível; o site continua funcionando. */
    }
  }

  function ensureRectsVisible() {
    const stageWidth = el.stage.clientWidth;
    if (!stageWidth) return;

    const anyVisible = config.rects.some(
      (rect) => rect.x < stageWidth && rect.x + rect.w > 0
    );

    if (!anyVisible) centerRects();
  }

  function centerRects() {
    const stageWidth = el.stage.clientWidth;
    if (!stageWidth) return;

    const minLeft = Math.min(...config.rects.map((rect) => rect.x));
    const maxRight = Math.max(...config.rects.map((rect) => rect.x + rect.w));
    const groupWidth = maxRight - minLeft;
    const targetLeft = Math.max(0, Math.round((stageWidth - groupWidth) / 2));
    const shift = targetLeft - minLeft;

    config.rects.forEach((rect) => {
      rect.x = Math.max(0, Math.round(rect.x + shift));
    });

    applyAllGeometry();
    syncInputs();
    saveConfigSoon();
  }

  function resetConfig() {
    config = defaultConfig();
    clearSelection();
    currentColors = [false, false, false];
    anim.elapsed = 0;
    anim.sequenceIndex = 0;
    anim.sequenceAccum = 0;
    anim.lastTs = null;
    applyAllGeometry();
    renderCurrentColors();
    syncControls();
    saveConfigNow();
  }

  function clampNumber(value, min, max, fallback) {
    const number = Number(value);
    if (!Number.isFinite(number)) return fallback;
    return Math.min(max, Math.max(min, number));
  }

  /* ------------------------------------------------------------------ */
  /* rendering                                                           */
  /* ------------------------------------------------------------------ */

  function applyGeometry(index) {
    const rect = config.rects[index];
    const node = el.rects[index];
    node.style.left = `${rect.x}px`;
    node.style.bottom = `${rect.y}px`;
    node.style.width = `${rect.w}px`;
    node.style.height = `${rect.h}px`;
  }

  function applyAllGeometry() {
    config.rects.forEach((_, index) => applyGeometry(index));
  }

  function colorsFromState(state) {
    return [Boolean(state & 4), Boolean(state & 2), Boolean(state & 1)];
  }

  function stateFromColors(colors) {
    return (colors[0] ? 4 : 0) | (colors[1] ? 2 : 0) | (colors[2] ? 1 : 0);
  }

  function blinkColorsAt(elapsed) {
    return config.rects.map((rect) => {
      const period = Math.max(LIMITS.period[0], rect.period);
      const phase = (rect.phase / 100) * period;
      return ((elapsed + phase) % period) < period / 2;
    });
  }

  function renderCurrentColors() {
    let colors;

    if (config.mode === "manual") {
      colors = config.manualColors.slice();
    } else if (config.mode === "blink") {
      colors = blinkColorsAt(anim.elapsed);
    } else {
      colors = colorsFromState(anim.sequenceIndex);
    }

    setColors(colors);
  }

  function setColors(colors) {
    const changed =
      colors[0] !== currentColors[0] ||
      colors[1] !== currentColors[1] ||
      colors[2] !== currentColors[2];

    if (!changed) return;
    currentColors = colors.slice();

    for (let index = 0; index < 3; index += 1) {
      const isBlack = colors[index];
      const rect = el.rects[index];
      rect.style.backgroundColor = isBlack ? "#000" : "#fff";
      rect.classList.toggle("is-black", isBlack);
      el.liveDots[index].classList.toggle("is-black", isBlack);
      el.chips[index].classList.toggle("is-black", isBlack);

      const bit = el.chips[index].querySelector(".chip-bit");
      if (bit) bit.textContent = isBlack ? "1" : "0";

      const sensorBit = el.cards[index]?.querySelector(".sensor-bit");
      if (sensorBit) sensorBit.textContent = isBlack ? "1" : "0";
    }

    const state = stateFromColors(colors);
    el.stateValue.textContent = String(state);

    el.stateButtons.forEach((button) => {
      const active = Number(button.dataset.state) === state;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    if (config.mode === "manual") syncColorToggles();
  }

  function syncControls() {
    el.modeButtons.forEach((button) => {
      const active = button.dataset.mode === config.mode;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    el.playback.hidden = config.mode === "manual";
    el.sequenceField.hidden = config.mode !== "sequence";

    el.guides.checked = config.showGuides;
    el.stage.classList.toggle("show-guides", config.showGuides);

    el.colorToggles.forEach((toggle) => {
      const disabled = config.mode !== "manual";
      toggle.classList.toggle("is-disabled", disabled);
      toggle.setAttribute("aria-disabled", String(disabled));
      $$(".color-btn", toggle).forEach((button) => {
        button.disabled = disabled;
      });
    });

    syncPlayback();
    syncInputs();
    syncColorToggles();

    const state = stateFromColors(currentColors);
    el.stateButtons.forEach((button) => {
      const active = Number(button.dataset.state) === state;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });

    updateSegIndicator();
  }

  function syncPlayback() {
    el.playBtn.classList.toggle("is-paused", !config.running);
    el.playLabel.textContent = config.running ? "Pausar" : "Continuar";
    el.playBtn.setAttribute("aria-pressed", String(config.running));
    el.playBtn.setAttribute(
      "aria-label",
      config.running ? "Pausar animação" : "Continuar animação"
    );
    syncLiveIndicator();
  }

  function syncInputs() {
    el.cards.forEach((card) => {
      syncRowInputs(Number(card.dataset.rect));
    });

    el.sequenceInput.value = String(config.sequenceInterval);
    el.guides.checked = config.showGuides;
  }

  function syncRowInputs(index) {
    const card = el.cards[index];
    if (!card) return;

    const rect = config.rects[index];
    $$("input[data-prop]", card).forEach((input) => {
      input.value = String(rect[input.dataset.prop]);
    });
  }

  function syncColorToggles() {
    el.colorToggles.forEach((toggle, index) => {
      $$(".color-btn", toggle).forEach((button) => {
        const isBlack = button.dataset.color === "on";
        button.classList.toggle("is-active", isBlack === config.manualColors[index]);
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* state grid, reading, selection and drag                             */
  /* ------------------------------------------------------------------ */

  function initStateDots() {
    el.stateButtons.forEach((button) => {
      const state = Number(button.dataset.state);
      const dots = button.querySelector(".state-dots");

      if (dots) {
        dots.replaceChildren();
        for (let index = 0; index < 3; index += 1) {
          const dot = document.createElement("i");
          dot.classList.toggle("is-on", Boolean(state & (4 >> index)));
          dots.appendChild(dot);
        }
      }

      const dec = button.querySelector(".state-dec");
      if (dec) dec.textContent = String(state);

      const bits = [state & 4 ? 1 : 0, state & 2 ? 1 : 0, state & 1 ? 1 : 0];
      button.setAttribute(
        "aria-label",
        `Estado ${bits.join("")}: L ${bits[0]}, C ${bits[1]}, R ${bits[2]}`
      );
    });
  }

  function updateSegIndicator() {
    if (!el.segIndicator) return;

    const active = el.modeButtons.find((button) => button.classList.contains("is-active"));
    if (!active) return;

    el.segIndicator.style.left = `${active.offsetLeft}px`;
    el.segIndicator.style.width = `${active.offsetWidth}px`;
  }

  function syncLiveIndicator() {
    if (!el.liveIndicator) return;

    const live = config.running && (config.mode === "blink" || config.mode === "sequence");
    el.liveIndicator.classList.toggle("is-live", live);

    const label = el.liveIndicator.querySelector("span");
    if (label) {
      label.textContent = live ? "ao vivo" : config.mode === "manual" ? "manual" : "pausado";
    }
  }

  function syncSurfaceMeta() {
    if (!el.surfaceSize) return;
    el.surfaceSize.textContent = `${Math.round(el.stage.clientWidth)} × ${Math.round(
      el.stage.clientHeight
    )}`;
  }

  function renderRuler() {
    if (!el.ruler) return;

    const width = el.stage.clientWidth;
    if (!width) return;

    const fragment = document.createDocumentFragment();
    const minor = 20;
    const major = 100;

    for (let x = 0; x <= width; x += minor) {
      const tick = document.createElement("span");
      tick.className = x % major === 0 ? "ruler-tick is-major" : "ruler-tick";
      tick.style.left = `${x}px`;
      fragment.appendChild(tick);

      if (x % major === 0) {
        const label = document.createElement("span");
        label.className = "ruler-label";
        label.style.left = `${x}px`;
        label.textContent = String(x);
        if (x === 0) label.classList.add("is-first");
        if (x + major > width) label.classList.add("is-last");
        fragment.appendChild(label);
      }
    }

    el.ruler.replaceChildren(fragment);
  }

  function selectRect(index) {
    selectedIndex = index;

    el.cards.forEach((card, cardIndex) => {
      card.classList.toggle("is-selected", cardIndex === index);
    });

    el.rects.forEach((rect, rectIndex) => {
      rect.classList.toggle("is-selected", rectIndex === index);
    });
  }

  function clearSelection() {
    if (selectedIndex === null) return;

    selectedIndex = null;
    el.cards.forEach((card) => card.classList.remove("is-selected"));
    el.rects.forEach((rect) => rect.classList.remove("is-selected"));
  }

  function setupAdjuster() {
    if (!el.adjuster) return;

    el.adjustButtons.forEach((button) => {
      button.addEventListener("click", () => setAdjuster(el.adjuster.hidden));
    });

    if (el.closeAdjust) {
      el.closeAdjust.addEventListener("click", () => setAdjuster(false));
    }
  }

  function setAdjuster(open) {
    if (!el.adjuster) return;

    const next = Boolean(open);
    el.adjuster.hidden = !next;
    el.stageDock?.classList.toggle("is-adjusting", next);
    el.adjustButtons.forEach((button) => {
      button.setAttribute("aria-expanded", String(next));
    });

    if (next && window.matchMedia("(max-width: 860px)").matches) {
      void el.adjuster.offsetHeight;
      const headerHeight = document.querySelector(".topbar")?.offsetHeight || 0;
      const target = el.adjuster.getBoundingClientRect().top + window.scrollY - headerHeight - 12;

      window.scrollTo(0, Math.max(0, target));
    }
  }

  function setupHelp() {
    if (!el.helpDialog) return;

    const open = () => {
      if (typeof el.helpDialog.showModal === "function") {
        if (!el.helpDialog.open) el.helpDialog.showModal();
      } else {
        el.helpDialog.setAttribute("open", "");
      }
    };

    const close = () => {
      if (typeof el.helpDialog.close === "function") el.helpDialog.close();
      else el.helpDialog.removeAttribute("open");
    };

    el.helpButtons.forEach((button) => button.addEventListener("click", open));
    if (el.closeHelp) el.closeHelp.addEventListener("click", close);
    el.helpDialog.addEventListener("click", (event) => {
      if (event.target === el.helpDialog) close();
    });
  }

  function setupSelection() {
    el.cards.forEach((card, index) => {
      card.addEventListener("click", () => selectRect(index));

      card.addEventListener("pointerenter", () => {
        el.rects[index]?.classList.add("is-hovered");
      });

      card.addEventListener("pointerleave", () => {
        el.rects[index]?.classList.remove("is-hovered");
      });
    });

    el.rects.forEach((rect, index) => {
      rect.addEventListener("pointerenter", () => {
        if (!document.body.classList.contains("robot-mode")) {
          el.cards[index]?.classList.add("is-hovered");
        }
      });

      rect.addEventListener("pointerleave", () => {
        el.cards[index]?.classList.remove("is-hovered");
      });
    });

    el.stage.addEventListener("click", (event) => {
      if (event.target === el.stage) clearSelection();
    });
  }

  function setupDrag() {
    el.rects.forEach((rect, index) => {
      rect.addEventListener("pointerdown", (event) => {
        if (event.button !== 0) return;
        if (event.target.closest(".rect-handle")) return;

        event.preventDefault();
        selectRect(index);

        const start = {
          pointerX: event.clientX,
          pointerY: event.clientY,
          x: config.rects[index].x,
          y: config.rects[index].y,
        };
        const maxX = Math.max(0, el.stage.clientWidth - config.rects[index].w);
        const maxY = Math.max(0, el.stage.clientHeight - config.rects[index].h);

        rect.setPointerCapture(event.pointerId);
        rect.classList.add("is-dragging");

        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - start.pointerX;
          const dy = moveEvent.clientY - start.pointerY;

          config.rects[index].x = Math.round(
            clampNumber(start.x + dx, 0, maxX, config.rects[index].x)
          );
          config.rects[index].y = Math.round(
            clampNumber(start.y - dy, 0, maxY, config.rects[index].y)
          );

          applyGeometry(index);
          syncRowInputs(index);
        };

        const onUp = () => {
          rect.classList.remove("is-dragging");
          if (rect.hasPointerCapture(event.pointerId)) {
            rect.releasePointerCapture(event.pointerId);
          }
          rect.removeEventListener("pointermove", onMove);
          rect.removeEventListener("pointerup", onUp);
          rect.removeEventListener("pointercancel", onUp);
          saveConfigSoon();
        };

        rect.addEventListener("pointermove", onMove);
        rect.addEventListener("pointerup", onUp);
        rect.addEventListener("pointercancel", onUp);
      });

      const handle = rect.querySelector(".rect-handle");
      if (!handle) return;

      handle.addEventListener("pointerdown", (event) => {
        if (event.button !== 0) return;

        event.preventDefault();
        event.stopPropagation();
        selectRect(index);

        const start = {
          pointerX: event.clientX,
          pointerY: event.clientY,
          x: config.rects[index].x,
          y: config.rects[index].y,
          w: config.rects[index].w,
          h: config.rects[index].h,
        };
        const top = start.y + start.h;
        const maxW = Math.max(4, el.stage.clientWidth - start.x);
        const maxH = Math.max(4, top);

        handle.setPointerCapture(event.pointerId);

        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - start.pointerX;
          const dy = moveEvent.clientY - start.pointerY;
          const width = Math.round(clampNumber(start.w + dx, 4, maxW, start.w));
          const height = Math.round(clampNumber(start.h + dy, 4, maxH, start.h));

          config.rects[index].w = width;
          config.rects[index].h = height;
          config.rects[index].y = top - height;

          applyGeometry(index);
          syncRowInputs(index);
        };

        const onUp = () => {
          if (handle.hasPointerCapture(event.pointerId)) {
            handle.releasePointerCapture(event.pointerId);
          }
          handle.removeEventListener("pointermove", onMove);
          handle.removeEventListener("pointerup", onUp);
          handle.removeEventListener("pointercancel", onUp);
          saveConfigSoon();
        };

        handle.addEventListener("pointermove", onMove);
        handle.addEventListener("pointerup", onUp);
        handle.addEventListener("pointercancel", onUp);
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* animation                                                           */
  /* ------------------------------------------------------------------ */

  function tick(timestamp) {
    if (anim.lastTs === null) anim.lastTs = timestamp;
    const delta = Math.min(120, Math.max(0, timestamp - anim.lastTs));
    anim.lastTs = timestamp;

    if (config.running && config.mode === "blink") {
      anim.elapsed += delta;
      setColors(blinkColorsAt(anim.elapsed));
    } else if (config.running && config.mode === "sequence") {
      anim.sequenceAccum += delta;
      const interval = Math.max(SEQUENCE_LIMITS[0], config.sequenceInterval);

      if (anim.sequenceAccum >= interval) {
        const steps = Math.floor(anim.sequenceAccum / interval);
        anim.sequenceAccum -= steps * interval;
        anim.sequenceIndex = (anim.sequenceIndex + steps) % 8;
        setColors(colorsFromState(anim.sequenceIndex));
      }
    }

    requestAnimationFrame(tick);
  }

  /* ------------------------------------------------------------------ */
  /* interactions                                                        */
  /* ------------------------------------------------------------------ */

  function setMode(mode) {
    if (!MODES.includes(mode) || mode === config.mode) return;

    if (mode === "manual") {
      config.manualColors = currentColors.slice();
    }

    config.mode = mode;
    anim.elapsed = 0;
    anim.sequenceIndex = 0;
    anim.sequenceAccum = 0;
    anim.lastTs = null;

    renderCurrentColors();
    syncControls();
    saveConfigSoon();
  }

  function applyState(state) {
    const colors = colorsFromState(state);
    config.manualColors = colors;
    config.mode = "manual";
    anim.lastTs = null;

    setColors(colors);
    syncControls();
    saveConfigSoon();
  }

  function setManualColor(index, isBlack) {
    config.manualColors[index] = Boolean(isBlack);
    config.mode = "manual";
    anim.lastTs = null;

    setColors(config.manualColors);
    syncControls();
    saveConfigSoon();
  }

  function setRunning(running) {
    config.running = Boolean(running);
    anim.lastTs = null;
    syncPlayback();
    renderCurrentColors();
    saveConfigSoon();
  }

  function bindEvents() {
    el.modeButtons.forEach((button) => {
      button.addEventListener("click", () => setMode(button.dataset.mode));
    });

    el.playBtn.addEventListener("click", () => setRunning(!config.running));

    el.sequenceInput.addEventListener("input", () => {
      const raw = el.sequenceInput.value.trim();
      if (raw === "") return;
      config.sequenceInterval = clampNumber(
        raw,
        SEQUENCE_LIMITS[0],
        SEQUENCE_LIMITS[1],
        config.sequenceInterval
      );
      saveConfigSoon();
    });

    el.sequenceInput.addEventListener("blur", () => {
      el.sequenceInput.value = String(config.sequenceInterval);
    });

    el.guides.addEventListener("change", () => {
      config.showGuides = el.guides.checked;
      el.stage.classList.toggle("show-guides", config.showGuides);
      saveConfigSoon();
    });

    el.cards.forEach((card) => {
      card.addEventListener("input", (event) => {
        const input = event.target.closest("input[data-prop]");
        if (!input) return;

        const raw = input.value.trim();
        if (raw === "") return;

        const index = Number(card.dataset.rect);
        const prop = input.dataset.prop;
        const limits = LIMITS[prop];
        if (!limits) return;

        const value = clampNumber(raw, limits[0], limits[1], config.rects[index][prop]);
        config.rects[index][prop] =
          prop === "period" || prop === "phase" ? value : Math.round(value);

        if (prop === "x" || prop === "y" || prop === "w" || prop === "h") {
          applyGeometry(index);
        } else if (config.mode === "blink" && !config.running) {
          renderCurrentColors();
        }

        saveConfigSoon();
      });

      card.addEventListener(
        "blur",
        (event) => {
          const input = event.target.closest("input[data-prop]");
          if (!input) return;
          const index = Number(card.dataset.rect);
          input.value = String(config.rects[index][input.dataset.prop]);
        },
        true
      );
    });

    el.colorButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const card = button.closest(".card");
        if (!card) return;
        setManualColor(Number(card.dataset.rect), button.dataset.color === "on");
      });
    });

    el.stateButtons.forEach((button) => {
      button.addEventListener("click", () => applyState(Number(button.dataset.state)));
    });

    el.robotBtn.addEventListener("click", enterRobotMode);
    el.centerBtn.addEventListener("click", centerRects);
    el.exitRobotBtn.addEventListener("click", () => exitRobotMode());

    el.resetButtons.forEach((button) => {
      button.addEventListener("click", () => {
        if (window.confirm("Restaurar todos os valores padrão?")) resetConfig();
      });
    });

    document.addEventListener("keydown", handleKeydown);
    document.addEventListener("mousemove", scheduleCursorHide, { passive: true });

    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        ensureRectsVisible();
        updateSegIndicator();
        renderRuler();
        syncSurfaceMeta();
      }, 200);
    });
    document.addEventListener("fullscreenchange", () => {
      if (!document.fullscreenElement && document.body.classList.contains("robot-mode")) {
        exitRobotMode(false);
      }
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        saveConfigNow();
      } else {
        anim.lastTs = null;
        if (document.body.classList.contains("robot-mode")) requestWakeLock();
      }
    });

    window.addEventListener("pagehide", saveConfigNow);
  }

  function handleKeydown(event) {
    if (el.helpDialog && el.helpDialog.open) return;

    const target = event.target;
    const isTextEntry =
      target instanceof Element &&
      (target.matches("textarea, select") ||
        target.isContentEditable ||
        (target.matches("input") &&
          !["checkbox", "radio", "button", "submit", "reset", "range"].includes(target.type)));
    const isControl =
      target instanceof Element &&
      target.matches('button, a, input[type="checkbox"], input[type="radio"]');

    if (event.key === "Escape") {
      if (el.adjuster && !el.adjuster.hidden) {
        event.preventDefault();
        setAdjuster(false);
        return;
      }

      if (document.body.classList.contains("robot-mode")) {
        event.preventDefault();
        exitRobotMode();
      }
      return;
    }

    if (isTextEntry) return;

    if (event.key === "f" || event.key === "F") {
      if (event.repeat) return;
      event.preventDefault();
      toggleRobotMode();
      return;
    }

    if (event.code === "Space" || event.key === " ") {
      if (isControl || config.mode === "manual") return;
      event.preventDefault();
      if (!event.repeat) setRunning(!config.running);
      return;
    }

    if (/^[0-7]$/.test(event.key)) {
      event.preventDefault();
      applyState(Number(event.key));
    }
  }

  /* ------------------------------------------------------------------ */
  /* robot mode                                                          */
  /* ------------------------------------------------------------------ */

  function toggleRobotMode() {
    if (document.body.classList.contains("robot-mode")) {
      exitRobotMode();
    } else {
      enterRobotMode();
    }
  }

  function enterRobotMode() {
    if (document.body.classList.contains("robot-mode")) return;

    if (el.adjuster && !el.adjuster.hidden) setAdjuster(false);

    document.body.classList.add("robot-mode");
    document.body.classList.remove("hide-cursor");
    scheduleCursorHide();

    if (document.documentElement.requestFullscreen && !document.fullscreenElement) {
      const request = document.documentElement.requestFullscreen();
      if (request && typeof request.catch === "function") request.catch(() => {});
    }

    requestWakeLock();
  }

  function exitRobotMode(exitFullscreen = true) {
    if (!document.body.classList.contains("robot-mode")) return;

    document.body.classList.remove("robot-mode", "hide-cursor");
    clearTimeout(cursorTimer);
    releaseWakeLock();

    if (exitFullscreen && document.fullscreenElement && document.exitFullscreen) {
      const exit = document.exitFullscreen();
      if (exit && typeof exit.catch === "function") exit.catch(() => {});
    }
  }

  function scheduleCursorHide() {
    if (!document.body.classList.contains("robot-mode")) return;

    document.body.classList.remove("hide-cursor");
    clearTimeout(cursorTimer);
    cursorTimer = window.setTimeout(() => {
      if (document.body.classList.contains("robot-mode")) {
        document.body.classList.add("hide-cursor");
      }
    }, 2500);
  }

  async function requestWakeLock() {
    if (!("wakeLock" in navigator) || wakeLock || wakeLockPending) return;

    wakeLockPending = true;
    try {
      const lock = await navigator.wakeLock.request("screen");
      if (!document.body.classList.contains("robot-mode")) {
        lock.release().catch(() => {});
        return;
      }
      wakeLock = lock;
      lock.addEventListener("release", () => {
        wakeLock = null;
      });
    } catch {
      wakeLock = null;
    } finally {
      wakeLockPending = false;
    }
  }

  function releaseWakeLock() {
    if (!wakeLock) return;
    const lock = wakeLock;
    wakeLock = null;
    lock.release().catch(() => {});
  }
})();
