/* Westerly Metals site behaviour. Towns data comes from towns.js (window.WM_TOWNS). */
(function () {
  "use strict";
  var OPEN = 6, CLOSE = 18; // 6am to 6pm, 7 days

  /* ---- open now (Melbourne time) ---- */
  function melbNow() {
    try {
      var parts = new Intl.DateTimeFormat("en-AU", { timeZone: "Australia/Melbourne", hour: "numeric", minute: "numeric", hour12: false }).formatToParts(new Date());
      var h = 0, m = 0;
      parts.forEach(function (p) { if (p.type === "hour") h = +p.value % 24; if (p.type === "minute") m = +p.value; });
      return h + m / 60;
    } catch (e) { return null; }
  }
  function paintStatus() {
    var t = melbNow();
    document.querySelectorAll("[data-status]").forEach(function (el) {
      var label = el.querySelector("span");
      if (t === null) { label.textContent = "Open 6am to 6pm, 7 days"; return; }
      var open = t >= OPEN && t < CLOSE;
      el.classList.toggle("is-open", open);
      if (open) {
        var left = CLOSE - t;
        label.textContent = left <= 1 ? "Open now · closes 6pm, last hour" : "Open now · until 6pm today";
      } else {
        label.textContent = t < OPEN ? "Closed · opens 6am today" : "Closed · opens 6am tomorrow";
      }
    });
  }
  paintStatus();
  setInterval(paintStatus, 60000);

  /* ---- menu ---- */
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("nav");
  if (btn && nav) {
    var setMenu = function (open) {
      nav.classList.toggle("open", open);
      document.body.classList.toggle("menu-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Close" : "Menu";
    };
    btn.addEventListener("click", function () { setMenu(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) { setMenu(false); btn.focus(); } });
    window.addEventListener("resize", function () { if (window.innerWidth > 1060 && nav.classList.contains("open")) setMenu(false); });
  }

  var towns = (window.WM_TOWNS || []).slice().sort(function (a, b) { return a.town.localeCompare(b.town); });
  function byName(n) { for (var i = 0; i < towns.length; i++) if (towns[i].town === n) return towns[i]; return null; }
  function fillSelect(sel, def) {
    if (!sel || sel.options.length) return;
    towns.forEach(function (t) {
      var o = document.createElement("option"); o.value = t.town; o.textContent = t.town;
      if (t.town === def) o.selected = true; sel.appendChild(o);
    });
  }
  function fmt(n, d) { return Number(n).toLocaleString("en-AU", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }); }
  function mins(m) {
    m = Math.round(m);
    if (m < 60) return m + "\u00a0min";
    var h = Math.floor(m / 60), r = m % 60;
    return h + "\u00a0hr" + (r ? " " + r + "\u00a0min" : "");
  }

  /* ---- quick check (home) ---- */
  var q = document.getElementById("quick-town");
  if (q) {
    fillSelect(q, "Warrnambool");
    var paintQuick = function () {
      var t = byName(q.value); if (!t) return;
      document.getElementById("q-us-km").textContent = fmt(t.yard_km);
      document.getElementById("q-us-t").textContent = mins(t.yard_min) + " one way";
      document.getElementById("q-mel-km").textContent = fmt(t.mel_km);
      document.getElementById("q-mel-t").textContent = mins(t.mel_min) + " one way, before city traffic";
      var km = 2 * (t.mel_km - t.yard_km), mn = 2 * (t.mel_min - t.yard_min);
      document.getElementById("q-save").innerHTML = "From " + t.town + " that's <b>" + fmt(km) + " km less driving</b>" +
        (mn >= 10 ? " and about <b>" + mins(mn) + "</b> back" : "") + " on every round trip.";
    };
    q.addEventListener("change", paintQuick); paintQuick();
  }

  /* ---- full calculator (savings page) ---- */
  var c = document.getElementById("calc");
  if (c) {
    var sel = document.getElementById("c-town");
    fillSelect(sel, "Warrnambool");
    var state = { lp100: 12 };
    var lp = document.getElementById("c-lp100");
    c.querySelectorAll(".seg button").forEach(function (b) {
      b.addEventListener("click", function () {
        c.querySelectorAll(".seg button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        lp.value = b.getAttribute("data-lp");
        calc();
      });
    });
    var loads = document.getElementById("c-loads"), loadsOut = document.getElementById("c-loads-out");
    ["c-town", "c-lp100", "c-fuel", "c-rate", "c-loads"].forEach(function (id) {
      var el = document.getElementById(id); el.addEventListener("input", calc); el.addEventListener("change", calc);
    });
    function num(id, d) { var v = parseFloat(document.getElementById(id).value); return isFinite(v) && v >= 0 ? v : d; }
    function calc() {
      var t = byName(sel.value); if (!t) return;
      var n = Math.max(1, Math.round(num("c-loads", 2)));
      loadsOut.textContent = n;
      var km = 2 * (t.mel_km - t.yard_km);
      var mn = Math.max(0, 2 * (t.mel_min - t.yard_min));
      var litres = km * num("c-lp100", 12) / 100;
      var fuel$ = litres * num("c-fuel", 2.65);
      var time$ = (mn / 60) * num("c-rate", 60);
      var trip$ = fuel$ + time$;
      var year = n * 12;
      document.getElementById("o-year").textContent = "$" + fmt(trip$ * year);
      var mini = document.getElementById("o-year-mini"); if (mini) mini.textContent = "$" + fmt(trip$ * year);
      document.getElementById("o-year-cap").textContent = "a year back, at " + n + " load" + (n > 1 ? "s" : "") + " a month from " + t.town;
      document.getElementById("o-km").textContent = fmt(km * year);
      document.getElementById("o-tanks").textContent = fmt(litres * year / 80, 1);
      document.getElementById("o-days").textContent = fmt(mn * year / 60 / 8, 1);
      document.getElementById("t-km").textContent = fmt(km) + " km";
      document.getElementById("t-time").textContent = mn >= 1 ? mins(mn) : "about the same";
      document.getElementById("t-fuel").textContent = fmt(litres, 1) + " L · $" + fmt(fuel$);
      document.getElementById("t-timev").textContent = "$" + fmt(time$);
      document.getElementById("t-total").textContent = "$" + fmt(trip$);
      var set = function (id, v) { var el = document.getElementById(id); if (el) el.textContent = v; };
      set("o-route", t.town + " to Moorabool: " + fmt(t.yard_km) + " km. " + t.town + " to Laverton North: " + fmt(t.mel_km) + " km.");
      set("c-us-km", fmt(t.yard_km)); set("c-us-t", mins(t.yard_min) + " one way");
      set("c-mel-km", fmt(t.mel_km)); set("c-mel-t", mins(t.mel_min) + " one way");
    }
    calc();
  }

  /* ---- enquiry form -> email ---- */
  document.querySelectorAll("form.enq").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var get = function (n) { var el = f.elements[n]; return el ? el.value.trim() : ""; };
      var subject = (f.getAttribute("data-subject") || "Enquiry") + (get("town") ? " · " + get("town") : "");
      var lines = [];
      ["name", "phone", "email", "town", "what", "size", "when"].forEach(function (k) {
        var el = f.elements[k]; if (el && el.value.trim()) lines.push((el.getAttribute("data-label") || k) + ": " + el.value.trim());
      });
      window.location.href = "mailto:" + f.getAttribute("data-to") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  });
})();
