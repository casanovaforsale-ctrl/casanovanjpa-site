/* Casanova Group site script. No libraries, no build step. */
(function () {
  "use strict";

  /* ---- Settings you may change ---------------------------------------- */
  var CONFIG = {
    // Google Analytics 4 measurement ID carried over from the Soloist site.
    gaId: "G-GJ8BW0RB7C",
    // Paste a Formspree form ID (the part after formspree.io/f/) to deliver
    // the contact form by email. Left empty, the form opens the visitor's
    // email app with the message filled in instead.
    formspreeId: "",
    email: "casanovaforsale@gmail.com"
  };

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---- Mobile menu ------------------------------------------------------ */
  var menuBtn = $(".menu-btn"), links = $("#nav-links");
  if (menuBtn && links) {
    menuBtn.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
      menuBtn.textContent = open ? "Close" : "Menu";
    });
    $$("a", links).forEach(function (a) { a.addEventListener("click", function () { links.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); menuBtn.textContent = "Menu"; }); });
  }

  /* ---- Analytics, only after the visitor accepts -------------------------- */
  function loadAnalytics() {
    if (!CONFIG.gaId || window.__gaLoaded) return;
    window.__gaLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + CONFIG.gaId;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", CONFIG.gaId);
  }
  var consent = store.get("cg-cookies");
  var banner = $("#cookie");
  if (consent === "yes") loadAnalytics();
  else if (consent !== "no" && banner) banner.hidden = false;
  if (banner) {
    $("#cookie-yes").addEventListener("click", function () { store.set("cg-cookies", "yes"); banner.hidden = true; loadAnalytics(); });
    $("#cookie-no").addEventListener("click", function () { store.set("cg-cookies", "no"); banner.hidden = true; });
  }

  /* ---- Video: load YouTube only when asked ------------------------------- */
  $$(".video-play[data-yt]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      var frame = btn.parentNode, id = btn.getAttribute("data-yt");
      var ifr = document.createElement("iframe");
      ifr.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
      ifr.title = btn.getAttribute("aria-label") || "Video";
      ifr.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
      ifr.allowFullscreen = true;
      e.preventDefault();
      frame.innerHTML = "";
      frame.appendChild(ifr);
    });
  });

  /* ---- Shared money helpers ---------------------------------------------- */
  var COUNTIES = [
    ["Camden County, NJ", 3.10], ["Gloucester County, NJ", 3.00], ["Salem County, NJ", 3.05],
    ["Burlington County, NJ", 2.65], ["Atlantic County, NJ", 2.55],
    ["Bucks County, PA", 1.55], ["Philadelphia County, PA", 1.00]
  ];
  function num(id) { var el = document.getElementById(id); return el ? (+el.value || 0) : 0; }
  function money(v) { return (v < 0 ? "-$" : "$") + Math.round(Math.abs(v)).toLocaleString("en-US"); }
  function pct(v) { return (v * 100).toFixed(2) + "%"; }
  function payment(loan, ratePct, years) {
    var k = years * 12; if (k <= 0) return 0;
    if (ratePct <= 0) return loan / k;
    var i = ratePct / 100 / 12;
    return loan * i / (1 - Math.pow(1 + i, -k));
  }
  function set(id, txt) { var el = document.getElementById(id); if (el) el.textContent = txt; }
  function fillCounties(sel, taxInput, onChange) {
    COUNTIES.forEach(function (c, i) { var o = document.createElement("option"); o.value = i; o.textContent = c[0]; sel.appendChild(o); });
    sel.value = 0;
    sel.addEventListener("change", function () { taxInput.value = COUNTIES[+sel.value][1].toFixed(2); onChange(); });
  }

  /* ---- First-time buyer: real monthly payment ---------------------------- */
  var pay = $("#pay");
  if (pay) {
    var runPay = function () {
      var price = num("p-price"), down = num("p-down") / 100, rate = num("p-rate"), term = num("p-term");
      var loan = price * (1 - down);
      var pi = payment(loan, rate, term);
      var tax = price * num("p-tax") / 100 / 12;
      var ins = num("p-ins") / 12;
      var pmi = down < 0.2 ? loan * num("p-pmi") / 100 / 12 : 0;
      var total = pi + tax + ins + pmi;
      var naive = pi + price * 0.011 / 12 + ins + pmi;
      set("p-total", money(total));
      set("p-pi", money(pi)); set("p-taxm", money(tax)); set("p-insm", money(ins)); set("p-pmim", money(pmi));
      set("p-cash", money(price * down + price * num("p-close") / 100));
      set("p-gap", money(Math.max(0, total - naive)));
      set("p-live", "Estimated monthly payment " + money(total));
    };
    fillCounties($("#p-cty"), $("#p-tax"), runPay);
    $$("input", pay).forEach(function (el) { el.addEventListener("input", runPay); });
    runPay();
  }

  /* ---- Investors: multi-family deal analyzer ----------------------------- */
  var deal = $("#deal");
  if (deal) {
    var tag = function (id, cls, txt) { var el = document.getElementById(id); el.className = "j " + cls; el.textContent = txt; };
    var runDeal = function () {
      var price = num("q-price"), units = num("q-units"), rent = num("q-rent"), vac = num("q-vac") / 100;
      var gsi = units * rent * 12, vl = gsi * vac, egi = gsi - vl;
      var otax = price * num("q-tax") / 100, oins = num("q-ins"), omaint = gsi * num("q-maint") / 100,
          omgmt = egi * num("q-mgmt") / 100, ocapx = gsi * num("q-capx") / 100, oother = num("q-other") * 12;
      var opex = otax + oins + omaint + omgmt + ocapx + oother, noi = egi - opex;
      var loan = price * (1 - num("q-down") / 100), ds = payment(loan, num("q-rate"), num("q-term")) * 12;
      var cf = noi - ds, invested = price * num("q-down") / 100 + price * num("q-close") / 100;
      var cap = price > 0 ? noi / price : 0, coc = invested > 0 ? cf / invested : 0, dscr = ds > 0 ? noi / ds : 0,
          grm = gsi > 0 ? price / gsi : 0, exr = egi > 0 ? opex / egi : 0;
      set("q-cf", money(cf / 12)); set("q-cf2", money(cf / 12));
      set("q-gsi", money(gsi / 12)); set("q-vl", "-" + money(vl / 12)); set("q-egi", money(egi / 12));
      set("q-otax", money(otax / 12)); set("q-oins", money(oins / 12)); set("q-omaint", money(omaint / 12));
      set("q-omgmt", money(omgmt / 12)); set("q-ocapx", money(ocapx / 12)); set("q-oother", money(oother / 12));
      set("q-noi", money(noi / 12)); set("q-ds", money(ds / 12));
      set("q-cap", pct(cap)); set("q-coc", pct(coc)); set("q-dscr", dscr.toFixed(2)); set("q-grm", grm.toFixed(1));
      set("q-exp", pct(exr)); set("q-cash", money(invested));
      tag("q-capj", cap >= .07 ? "good" : (cap >= .055 ? "mid" : "bad"), cap >= .07 ? "Strong" : (cap >= .055 ? "Workable" : "Thin"));
      tag("q-cocj", coc >= .08 ? "good" : (coc >= .04 ? "mid" : "bad"), coc >= .08 ? "Strong" : (coc >= .04 ? "Modest" : "Weak"));
      tag("q-dscrj", dscr >= 1.25 ? "good" : (dscr >= 1.2 ? "mid" : "bad"), dscr >= 1.25 ? "Lender-ready" : (dscr >= 1.2 ? "Borderline" : "Will not finance"));
      set("q-live", "Monthly cash flow " + money(cf / 12) + ", cap rate " + pct(cap) + ", DSCR " + dscr.toFixed(2));
    };
    fillCounties($("#q-cty"), $("#q-tax"), runDeal);
    $$("input", deal).forEach(function (el) { el.addEventListener("input", runDeal); });
    runDeal();
  }

  /* ---- Contact form ------------------------------------------------------ */
  var form = $("#contact-form");
  if (form) {
    var status = $("#form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (form.elements["company"] && form.elements["company"].value) return; // spam trap
      var data = { name: form.elements["name"].value, email: form.elements["email"].value, phone: form.elements["phone"].value, message: form.elements["message"].value };
      status.className = "form-status";
      if (CONFIG.formspreeId) {
        status.textContent = "Sending…";
        fetch("https://formspree.io/f/" + CONFIG.formspreeId, { method: "POST", headers: { "Accept": "application/json", "Content-Type": "application/json" }, body: JSON.stringify(data) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); status.className = "form-status ok"; status.textContent = "Talk soon! Nick will get back to you shortly."; })
          .catch(function () { status.className = "form-status err"; status.textContent = "That did not go through. Please call 856-888-4334 or email " + CONFIG.email + "."; });
      } else {
        var body = "Name: " + data.name + "\nPhone: " + data.phone + "\nEmail: " + data.email + "\n\n" + data.message;
        window.location.href = "mailto:" + CONFIG.email + "?subject=" + encodeURIComponent("Website enquiry from " + data.name) + "&body=" + encodeURIComponent(body);
        status.className = "form-status ok";
        status.textContent = "Your email app should open with the message filled in. If it does not, email " + CONFIG.email + " or call 856-888-4334.";
      }
    });
  }

  /* ---- Footer year -------------------------------------------------------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();

/* ---- Count-up numbers in the at-a-glance row ------------------------------ */
(function () {
  "use strict";
  var els = Array.prototype.slice.call(document.querySelectorAll("[data-count]"));
  if (!els.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  function run(el) {
    var target = parseFloat(el.getAttribute("data-count")), dec = +(el.getAttribute("data-dec") || 0), t0 = null, dur = 1600;
    function frame(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = (target * e).toFixed(dec);
      if (k < 1) requestAnimationFrame(frame); else el.textContent = target.toFixed(dec);
    }
    requestAnimationFrame(frame);
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { run(en.target); io.unobserve(en.target); } });
  }, { threshold: 0.6 });
  els.forEach(function (el) { io.observe(el); });
})();

/* ---- Desktop depth: trailing cursor ring and 3D tilt on cards ------------- */
(function () {
  "use strict";
  var mq = function (q) { return window.matchMedia && window.matchMedia(q).matches; };
  if (!mq("(hover: hover) and (pointer: fine)") || mq("(prefers-reduced-motion: reduce)")) return;
  document.documentElement.classList.add("has-depth");

  var ring = document.createElement("div");
  ring.className = "cursor-ring";
  ring.setAttribute("aria-hidden", "true");
  document.body.appendChild(ring);
  var mx = -100, my = -100, rx = mx, ry = my, running = false;
  function loop() {
    rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18;
    ring.style.transform = "translate3d(" + rx + "px," + ry + "px,0)";
    if (Math.abs(mx - rx) + Math.abs(my - ry) > 0.3) requestAnimationFrame(loop); else running = false;
  }
  document.addEventListener("mousemove", function (e) {
    mx = e.clientX; my = e.clientY; ring.classList.remove("is-out");
    ring.classList.toggle("is-link", !!e.target.closest("a, button, summary, select, label, [role=button]"));
    if (!running) { running = true; requestAnimationFrame(loop); }
  }, { passive: true });
  document.addEventListener("mouseleave", function () { ring.classList.add("is-out"); });
  document.addEventListener("mousedown", function () { ring.classList.add("is-down"); });
  document.addEventListener("mouseup", function () { ring.classList.remove("is-down"); });

  var MAX = 6;
  Array.prototype.forEach.call(document.querySelectorAll(".hero-photo, .service-img, .post-card, .video-frame, .cov-map"), function (el) {
    el.setAttribute("data-tilt", "");
    el.addEventListener("mousemove", function (e) {
      var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      el.classList.add("tilting");
      el.style.setProperty("--ry", ((x - 0.5) * 2 * MAX).toFixed(2) + "deg");
      el.style.setProperty("--rx", ((0.5 - y) * 2 * MAX).toFixed(2) + "deg");
      el.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
      el.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
    });
    el.addEventListener("mouseleave", function () {
      el.classList.remove("tilting");
      el.style.setProperty("--rx", "0deg"); el.style.setProperty("--ry", "0deg");
    });
  });
})();

/* ---- Coverage map, key-tag reviews and the live 9:14 PM scene ------------- */
(function () {
  "use strict";
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canWatch = "IntersectionObserver" in window;
  if (!calm && canWatch) document.documentElement.classList.add("js-anim");
  function whenSeen(el, fn, threshold) {
    if (!canWatch) { fn(); return; }
    var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { fn(); io.disconnect(); } }, { threshold: threshold || 0.3 });
    io.observe(el);
  }

  /* Coverage map: draw on scroll, pick a county from the map or the buttons */
  var map = document.getElementById("coverage");
  if (map) {
    var svg = map.querySelector(".cm-svg");
    whenSeen(svg, function () { svg.classList.add("is-drawn"); }, 0.25);
    var current = "camden";
    var pick = function (key) {
      current = key;
      $$(".cov-list button", map).forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-county") === key); b.setAttribute("aria-pressed", b.getAttribute("data-county") === key ? "true" : "false"); });
      $$(".cm-county", map).forEach(function (p) { p.classList.toggle("is-on", p.getAttribute("data-county") === key); });
      $$(".cov-info", map).forEach(function (d) { d.classList.toggle("is-on", d.getAttribute("data-for") === key); });
    };
    $$(".cov-list button", map).forEach(function (b) { b.addEventListener("click", function () { pick(b.getAttribute("data-county")); }); });
    $$(".cm-county", map).forEach(function (p) {
      p.addEventListener("click", function () { pick(p.getAttribute("data-county")); });
      p.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(p.getAttribute("data-county")); } });
    });
    pick(current);
    var run = map.querySelector(".cov-run");
    if (run) run.addEventListener("click", function () {
      var info = map.querySelector('.cov-info[data-for="' + current + '"]'), idx = info ? info.getAttribute("data-idx") : null;
      ["p-cty", "q-cty"].forEach(function (id) {
        var sel = document.getElementById(id);
        if (sel && idx !== null) { sel.value = idx; sel.dispatchEvent(new Event("change")); }
      });
    });
  }

  /* Key tags: turn over to read the review */
  $$(".keytag").forEach(function (tag) {
    var front = tag.querySelector(".keytag-flip:not(.keytag-flip-back)"), back = tag.querySelector(".keytag-flip-back");
    var setFlip = function (on) {
      tag.classList.toggle("is-flipped", on);
      front.setAttribute("aria-expanded", on ? "true" : "false");
      (on ? back : front).focus({ preventScroll: true });
    };
    front.addEventListener("click", function () { setFlip(true); });
    back.addEventListener("click", function () { setFlip(false); });
  });

  /* 9:14 PM: each step lights up as it scrolls past, and the phone follows along */
  var steps = $$("#always-on .timeline.live .tl-step");
  if (steps.length && canWatch && !calm) {
    var clock = document.querySelector(".phone-time"), day = document.querySelector(".phone-day");
    var bubs = $$(".phone .bub");
    var TIMES = [["Tuesday", "9:14"], ["Tuesday", "9:14"], ["Tuesday", "9:17"], ["Tuesday", "9:17"], ["Tuesday", "9:18"], ["Wednesday", "8:00"]];
    var reached = -1;
    var reach = function (n) {
      if (n <= reached) return;
      for (var k = reached + 1; k <= n; k++) { steps[k].classList.add("on"); if (bubs[k]) bubs[k].classList.add("show"); }
      reached = n;
      var t = TIMES[Math.min(n, TIMES.length - 1)];
      if (clock && clock.textContent !== t[1]) { clock.textContent = t[1]; clock.classList.remove("tick"); void clock.offsetWidth; clock.classList.add("tick"); }
      if (day) day.textContent = t[0];
    };
    steps.forEach(function (s) { s.classList.remove("on"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) reach(steps.indexOf(en.target)); });
    }, { rootMargin: "0px 0px -45% 0px", threshold: 0 });
    steps.forEach(function (s) { io.observe(s); });
  }
})();
