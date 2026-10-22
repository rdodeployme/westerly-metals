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
  /* ---- town picker: type to search, scrolling list. The native select stays in the
     page (hidden) and gets a "change" event, so the calculators work unchanged. ---- */
  function townPicker(sel) {
    if (!sel || sel.getAttribute("data-tp")) return;
    sel.setAttribute("data-tp", "1");
    var id = sel.id, lbl = document.querySelector('label[for="' + id + '"]');
    var wrap = document.createElement("div"); wrap.className = "tp";
    var inp = document.createElement("input");
    inp.type = "text"; inp.className = "tp-in"; inp.id = id + "-q"; inp.autocomplete = "off"; inp.spellcheck = false;
    inp.setAttribute("role", "combobox"); inp.setAttribute("aria-autocomplete", "list");
    inp.setAttribute("aria-expanded", "false"); inp.setAttribute("aria-controls", id + "-list");
    inp.placeholder = "Type your town";
    var btn = document.createElement("button");
    btn.type = "button"; btn.className = "tp-btn"; btn.tabIndex = -1; btn.setAttribute("aria-label", "Show all towns");
    var list = document.createElement("ul");
    list.className = "tp-list"; list.id = id + "-list"; list.setAttribute("role", "listbox"); list.hidden = true;
    if (lbl) { lbl.htmlFor = inp.id; list.setAttribute("aria-labelledby", lbl.id || (lbl.id = id + "-l")); }
    sel.parentNode.insertBefore(wrap, sel);
    wrap.appendChild(inp); wrap.appendChild(btn); wrap.appendChild(list); wrap.appendChild(sel);
    sel.classList.add("tp-native"); sel.tabIndex = -1; sel.setAttribute("aria-hidden", "true");
    inp.value = sel.value;

    var shown = [], act = -1;
    var esc = function (t) { return t.replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); };
    function render(q) {
      q = (q || "").trim().toLowerCase();
      var starts = [], has = [];
      towns.forEach(function (t) {
        var n = t.town.toLowerCase();
        if (!q || n.indexOf(q) === 0) starts.push(t); else if (n.indexOf(q) > 0) has.push(t);
      });
      shown = starts.concat(has);
      if (!shown.length) {
        list.innerHTML = '<li class="tp-none" role="option" aria-disabled="true">No town by that name. Try the nearest big town.</li>';
        act = -1; return;
      }
      list.innerHTML = shown.map(function (t, i) {
        var n = esc(t.town), k = q ? t.town.toLowerCase().indexOf(q) : -1;
        if (k >= 0) n = esc(t.town.slice(0, k)) + "<mark>" + esc(t.town.slice(k, k + q.length)) + "</mark>" + esc(t.town.slice(k + q.length));
        var cur = t.town === sel.value;
        return '<li role="option" id="' + id + '-o' + i + '" data-i="' + i + '" aria-selected="' + cur + '"' + (cur ? ' class="cur"' : "") +
          '><span>' + n + '</span><small>' + fmt(t.yard_km) + " km</small></li>";
      }).join("");
      var c = -1; shown.forEach(function (t, i) { if (t.town === sel.value) c = i; });
      setAct(q ? 0 : Math.max(c, 0), !q);
    }
    function setAct(i, centre) {
      var items = list.querySelectorAll("li[data-i]");
      if (!items.length) { act = -1; return; }
      act = (i + items.length) % items.length;
      items.forEach(function (li, j) { li.classList.toggle("act", j === act); });
      var li = items[act];
      inp.setAttribute("aria-activedescendant", li.id);
      if (centre) list.scrollTop = li.offsetTop - list.clientHeight / 2 + li.offsetHeight / 2;
      else if (li.offsetTop < list.scrollTop) list.scrollTop = li.offsetTop - 6;
      else if (li.offsetTop + li.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = li.offsetTop + li.offsetHeight - list.clientHeight + 6;
    }
    function open(all) {
      var was = list.hidden;
      list.hidden = false; wrap.classList.add("open"); inp.setAttribute("aria-expanded", "true");
      render(all ? "" : inp.value);
      if (was) {
        // make room for the list: keep it clear of the bottom call bar on phones
        var cb = document.querySelector(".callbar"), cbh = cb && getComputedStyle(cb).display !== "none" ? cb.offsetHeight : 0;
        var over = list.getBoundingClientRect().bottom - (window.innerHeight - cbh - 12);
        var room = inp.getBoundingClientRect().top - 96;
        if (over > 0 && room > 0) window.scrollBy({ top: Math.min(over, room), behavior: "smooth" });
      }
    }
    function close() {
      list.hidden = true; wrap.classList.remove("open"); inp.setAttribute("aria-expanded", "false"); inp.removeAttribute("aria-activedescendant");
    }
    function choose(t) {
      if (t && t.town !== sel.value) { sel.value = t.town; sel.dispatchEvent(new Event("change", { bubbles: true })); }
      inp.value = sel.value; close();
    }
    inp.addEventListener("focus", function () { open(true); inp.select(); setTimeout(function () { if (inp.value === sel.value) inp.select(); }, 0); });
    inp.addEventListener("click", function () { if (list.hidden) { open(true); inp.select(); } });
    inp.addEventListener("input", function () { open(false); });
    inp.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault(); if (list.hidden) { open(true); return; }
        setAct(act + (e.key === "ArrowDown" ? 1 : -1));
      } else if (e.key === "Enter") {
        if (!list.hidden) { e.preventDefault(); choose(shown[act]); }
      } else if (e.key === "Escape") {
        if (!list.hidden) { e.preventDefault(); inp.value = sel.value; close(); }
      } else if (e.key === "Tab") {
        if (!list.hidden && inp.value !== sel.value && shown[act]) choose(shown[act]); else { inp.value = sel.value; close(); }
      }
    });
    inp.addEventListener("blur", function () {
      setTimeout(function () {
        if (wrap.contains(document.activeElement)) return;
        var exact = byName((inp.value || "").trim().replace(/^\w/, function (c) { return c.toUpperCase(); }));
        if (!exact) towns.forEach(function (t) { if (t.town.toLowerCase() === inp.value.trim().toLowerCase()) exact = t; });
        if (exact) choose(exact); else { inp.value = sel.value; close(); }
      }, 120);
    });
    list.addEventListener("mousedown", function (e) { e.preventDefault(); });
    list.addEventListener("click", function (e) {
      var li = e.target.closest("li[data-i]"); if (li) choose(shown[+li.getAttribute("data-i")]);
    });
    btn.addEventListener("mousedown", function (e) { e.preventDefault(); });
    btn.addEventListener("click", function () {
      if (list.hidden) { inp.focus(); open(true); } else { inp.value = sel.value; close(); }
    });
    document.addEventListener("pointerdown", function (e) { if (!wrap.contains(e.target) && !list.hidden) { inp.value = sel.value; close(); } });
    sel.addEventListener("change", function () { if (document.activeElement !== inp) inp.value = sel.value; });
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
    fillSelect(q, "Warrnambool"); townPicker(q);
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
    fillSelect(sel, "Warrnambool"); townPicker(sel);
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

  /* ---- prices: board + load estimate (rates from rates.js) ---- */
  var board = document.querySelector(".board");
  if (board) {
    var R = window.WM_RATES || { rates: {}, fees: {} };
    var rates = R.rates || {}, fees = R.fees || {};
    var money = function (n, dp) { return "$" + Number(n).toLocaleString("en-AU", { minimumFractionDigits: dp, maximumFractionDigits: dp }); };
    var has = function (v) { return typeof v === "number" && isFinite(v) && v >= 0; };
    var anyRate = Object.keys(rates).some(function (k) { return has(rates[k]); });

    // stamp
    var stamp = document.getElementById("rates-stamp");
    if (stamp && R.updated) {
      stamp.classList.add("is-live");
      stamp.querySelector("span").innerHTML = "Rates per kg · <b>" + String(R.updated).replace(/[<>&]/g, "") + "</b>";
    } else if (stamp && !anyRate) {
      stamp.querySelector("span").textContent = "Call for today's rates · per kg, clean and sorted";
    }
    // fill prices
    board.querySelectorAll("[data-rate]").forEach(function (el) {
      var v = rates[el.getAttribute("data-rate")];
      if (has(v)) el.innerHTML = '<span class="amt">' + money(v, 2) + '</span><span class="per">/kg</span>';
    });
    board.querySelectorAll("[data-fee]").forEach(function (el) {
      var v = fees[el.getAttribute("data-fee")];
      if (has(v)) el.innerHTML = '<span class="amt">' + money(v, 0) + '</span><span class="per">each</span>';
    });
    // tabs
    var tabs = board.querySelectorAll('[role="tab"]');
    var pick = function (t) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
      });
    };
    tabs.forEach(function (t, i) {
      t.tabIndex = i === 0 ? 0 : -1;
      t.addEventListener("click", function () { pick(t); t.scrollIntoView({ block: "nearest", inline: "nearest" }); });
      t.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (!d) return;
        e.preventDefault(); var n = tabs[(i + d + tabs.length) % tabs.length]; pick(n); n.focus();
      });
    });

    // estimator
    var est = document.getElementById("est");
    if (est) {
      var mode = "drop";
      var townSel = document.getElementById("est-town");
      fillSelect(townSel, "Warrnambool"); townPicker(townSel);
      var rows = est.querySelectorAll(".mrow");
      var kgOf = function (row) { var v = parseFloat(row.querySelector(".kg-in").value); return isFinite(v) && v > 0 ? Math.round(v) : 0; };
      var setKg = function (row, v) { row.querySelector(".kg-in").value = Math.max(0, Math.round(v)); calcEst(); };
      rows.forEach(function (row) {
        row.querySelector(".kg-minus").addEventListener("click", function () { setKg(row, kgOf(row) - 10); });
        row.querySelector(".kg-plus").addEventListener("click", function () { setKg(row, kgOf(row) + 10); });
        row.querySelector(".kg-in").addEventListener("input", calcEst);
        row.querySelector(".kg-in").addEventListener("focus", function () { if (this.value === "0") this.select(); });
        row.querySelector(".mgrade").addEventListener("change", calcEst);
      });
      est.querySelectorAll("#est-mode button").forEach(function (b) {
        b.addEventListener("click", function () {
          mode = b.getAttribute("data-mode");
          est.querySelectorAll("#est-mode button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          calcEst();
        });
      });
      townSel.addEventListener("change", calcEst);
      document.getElementById("est-clear").addEventListener("click", function () { rows.forEach(function (r) { r.querySelector(".kg-in").value = 0; }); calcEst(); });
      calcEst();
    }
  }

  function calcEst() {
    var est = document.getElementById("est"); if (!est) return;
    var R = window.WM_RATES || { rates: {} }, rates = R.rates || {};
    var has = function (v) { return typeof v === "number" && isFinite(v) && v >= 0; };
    var money0 = function (n) { return "$" + Math.round(n).toLocaleString("en-AU"); };
    var mode = est.querySelector('#est-mode button[aria-pressed="true"]').getAttribute("data-mode");
    var t = byName(document.getElementById("est-town").value);
    var lines = [], kg = 0, value = 0, priced = true;
    est.querySelectorAll(".mrow").forEach(function (row) {
      var v = parseFloat(row.querySelector(".kg-in").value); v = isFinite(v) && v > 0 ? Math.round(v) : 0;
      row.classList.toggle("has", v > 0);
      if (!v) return;
      var sel = row.querySelector(".mgrade"), gid = sel.value, gname = sel.options[sel.selectedIndex].text;
      var r = rates[gid];
      kg += v;
      if (has(r)) { value += v * r; lines.push([gname, fmt(v) + " kg · " + money0(v * r)]); }
      else { priced = false; lines.push([gname, fmt(v) + " kg"]); }
    });
    var val = document.getElementById("est-val"), cap = document.getElementById("est-cap"), lbl = document.getElementById("est-lbl");
    document.getElementById("est-lines").innerHTML = lines.map(function (l) { return "<li><span>" + l[0] + "</span><b>" + l[1] + "</b></li>"; }).join("");
    document.getElementById("est-kg").textContent = fmt(kg) + " kg";
    val.classList.remove("is-call");
    if (!kg) {
      lbl.textContent = "Your estimate"; val.textContent = "$0"; cap.textContent = "Add some kilos to get started";
    } else if (priced) {
      lbl.textContent = "Your estimate";
      val.textContent = value < 20 ? money0(value) : money0(value * 0.9) + "–" + money0(value);
      cap.textContent = "For about " + fmt(kg) + " kg at our listed rates";
    } else {
      lbl.textContent = "Your load"; val.classList.add("is-call"); val.textContent = fmt(kg) + " kg";
      cap.textContent = "Call for today's rate on this load";
    }
    // trip line + buttons
    var trip = document.getElementById("est-trip"), cta = document.getElementById("est-cta");
    var phoneBtn = '<a class="btn btn-amber" href="tel:0418524602">Call for today\'s rate</a>';
    if (mode === "drop") {
      if (t) {
        var save = 2 * (t.mel_km - t.yard_km);
        trip.innerHTML = "Moorabool is <b>" + fmt(t.yard_km) + " km</b> from " + t.town + (save > 0 ? ", <b>" + fmt(save) + " km less</b> per round trip than Laverton North." : ".") + " Open 6am to 6pm, 7&nbsp;days.";
      }
      cta.innerHTML = (kg && !priced ? phoneBtn : "") + '<a class="btn btn-line" href="https://www.google.com/maps/dir/?api=1&destination=Atkinsons+Road%2C+Moorabool+VIC+3213" target="_blank" rel="noopener">Get directions</a>';
    } else {
      trip.innerHTML = t ? "We'll collect from <b>" + t.town + "</b>. Pickups are quoted for the trip, and we confirm the fee before we come." : "";
      var what = lines.map(function (l) { return l[0] + " (" + l[1].split(" · ")[0].replace(" ", " ") + ")"; }).join(", ");
      var href = "pickups.html?town=" + encodeURIComponent(t ? t.town : "") + (what ? "&what=" + encodeURIComponent(what) : "") + "#enquire";
      cta.innerHTML = '<a class="btn btn-amber" href="' + href + '">Ask for a pickup</a>' + (kg && !priced ? '<a class="btn btn-line" href="tel:0418524602">Call for today\'s rate</a>' : "");
    }
    document.getElementById("est-note").innerHTML = mode === "drop"
      ? "Final price set on the scale at the yard. Paid by bank transfer, so bring photo&nbsp;ID."
      : "Final price set on the scale at the yard, less the quoted pickup fee. Paid by bank&nbsp;transfer.";
  }

  /* ---- pickups form: prefill from the load estimate ---- */
  (function () {
    var f = document.querySelector('form.enq[data-subject="Pickup enquiry"]'); if (!f) return;
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("town") && f.elements.town && !f.elements.town.value) f.elements.town.value = q.get("town").slice(0, 80);
      if (q.get("what") && f.elements.what && !f.elements.what.value) f.elements.what.value = q.get("what").slice(0, 600);
    } catch (e) {}
  })();

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
