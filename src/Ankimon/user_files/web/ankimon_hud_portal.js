// user_files/web/ankimon_hud_portal.js
(function initAnkimonHUD() {
  try {
    if (window.__ankimonHud) return;

    // Create a fixed container near the bottom center
    const hostId = "ankimon-hud-host";
    const existing = document.getElementById(hostId);
    if (existing) existing.remove();

    const host = document.createElement("div");
    host.id = hostId;

    const force = (el, props) => {
      if (!el) return;
      for (const [k, v] of Object.entries(props)) {
        try { el.style.setProperty(k, v, "important"); } catch (e) {}
      }
    };

    // Pin to viewport bottom-center like the legacy HUD (you can tweak sizes later)
    force(host, {
      all: "initial",
      position: "fixed",
      left: "50%",
      bottom: "16px",
      transform: "translateX(-50%)",
      width: "min(900px, 96vw)",
      height: "auto",
      "z-index": "2147483646",
      background: "transparent",
      "pointer-events": "none", // HUD outer lets clicks pass; inner can enable if needed
      display: "block",
      isolation: "isolate",
      filter: "invert(1) hue-rotate(180deg) saturate(0.555) contrast(0.833)" // Counter-filter
    });

    // Append outside card flow to avoid scroll/overflow containers
    (document.documentElement || document.body).appendChild(host);

    // Closed shadow root = max isolation
    const root = host.attachShadow({ mode: "closed" });

    // Base reset inside the shadow; the dynamic CSS you provide will be appended on update()
    const baseStyle = document.createElement("style");
    baseStyle.textContent = `
      :host { all: initial !important; }
      #hud-root {
        all: initial !important;
        display: block !important;
        position: relative !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
      }
      *, *::before, *::after {
        box-sizing: border-box !important;
        animation: none !important;
        transition: none !important;
        filter: none !important;
        /* Explicitly unset filter and transform for all elements inside shadow DOM */
        filter: none !important;
      }
      img { /* Target images specifically within the shadow DOM */
        filter: none !important;
      }
    `;

    const hudRoot = document.createElement("div");
    hudRoot.id = "hud-root";

    root.appendChild(baseStyle);
    root.appendChild(hudRoot);

    // Public API used by Python to render/update HUD content
    window.__ankimonHud = {
      update: (html, css) => {
        try {
          hudRoot.textContent = "";

          const wrapper = document.createElement("div");
          wrapper.style.pointerEvents = "auto"; // Allow interaction inside HUD if needed

          if (css && css.length) {
            const dynStyle = document.createElement("style");
            dynStyle.textContent = css;
            hudRoot.appendChild(dynStyle);
          }

          wrapper.innerHTML = html || "";
          hudRoot.appendChild(wrapper);
        } catch (e) {
          try { console.error("Ankimon HUD update failed:", e); } catch (_) {}
        }
      },
      clear: () => {
        try { hudRoot.textContent = ""; } catch (_) {}
      }
    };
  } catch (e) {
    try { console.error("Ankimon HUD init failed:", e); } catch (_) {}
  }
})();