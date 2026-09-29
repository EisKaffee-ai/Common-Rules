
(function(){
  var $ = function(s, r){ return (r || document).querySelector(s); };
  var $$ = function(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var VIEWS = ["tree", "kanban", "board", "list"];
  // proposal 30, P-11: one filter bar, at the top, governing all four views
  // (Tree/Kanban/Board/List) alike. State (view, every filter, the search
  // text and the Pending toggle) persists per viewer in localStorage --
  // every read and write of it is wrapped in try/catch, and a throwing or
  // empty store still renders the page correctly (Tree, no filters, the
  // built-in defaults below).
  var state = {proposal: "", statuses: [], owner: "", tier: "", group: "", q: "",
               view: "tree", pending: false, showFinished: false};
  try {
    var v = localStorage.getItem("tracker-view");
    if (VIEWS.indexOf(v) >= 0) state.view = v;
  } catch (e) {}
  try {
    var raw = localStorage.getItem("tracker-filters");
    var f = raw ? JSON.parse(raw) : null;
    if (f && typeof f === "object") {
      if (typeof f.proposal === "string") state.proposal = f.proposal;
      if (Array.isArray(f.statuses)) state.statuses = f.statuses.filter(function(s){ return typeof s === "string"; });
      if (typeof f.owner === "string") state.owner = f.owner;
      if (typeof f.tier === "string") state.tier = f.tier;
      if (typeof f.group === "string") state.group = f.group;
      if (typeof f.q === "string") state.q = f.q;
      if (typeof f.pending === "boolean") state.pending = f.pending;
      if (typeof f.showFinished === "boolean") state.showFinished = f.showFinished;
    }
  } catch (e) {}
  function persist(){
    try { localStorage.setItem("tracker-view", state.view); } catch (e) {}
    try {
      localStorage.setItem("tracker-filters", JSON.stringify({
        proposal: state.proposal, statuses: state.statuses, owner: state.owner, tier: state.tier,
        group: state.group, q: state.q, pending: state.pending, showFinished: state.showFinished
      }));
    } catch (e) {}
  }
  // Pending hides everything terminal (done or deferred), at every level, and always wins
  // over "Show finished" -- the two controls can never disagree because
  // "Show finished" is forced off (and disabled) for as long as Pending is
  // on. With Pending off, "Show finished" decides done work exactly as
  // before.
  function hideFinished(){ return state.pending || !state.showFinished; }
  function isTerminal(el){ return el && (el.dataset.group === "done" || el.dataset.status === "deferred"); }
  var items = $$("[data-item]");
  var searchById = {};
  $$("article[data-item],[data-item].item-row").forEach(function(card){ searchById[card.dataset.id] = card.dataset.search || ""; });
  var rows = $$("tr[data-item]");
  rows.forEach(function(row){ row.dataset.search = searchById[row.dataset.id] || ""; });
  function match(el, ignoreStatus, ignoreFinished){
    var d = el.dataset;
    if (state.proposal && d.proposal !== state.proposal) return false;
    if (!ignoreStatus && state.statuses.length && state.statuses.indexOf(d.status) < 0) return false;
    if (state.owner && d.owner !== state.owner) return false;
    if (state.tier && d.tier !== state.tier) return false;
    if (state.group && d.group !== state.group) return false;
    if (!ignoreFinished && hideFinished() && isTerminal(el) && state.group !== "done") return false;
    if (state.q && (d.search || "").indexOf(state.q) < 0) return false;
    return true;
  }
  // Every part (or sub-part, at any depth) in the Proposals tree, filtered
  // on its own: a part that does not match the active status/Pending/search
  // filters is hidden without touching its siblings. A part with sub-parts
  // (a <details class="prow-details">) stays visible when it, or any
  // descendant, matches -- and opens to reveal the match.
  function partOwnMatches(row){
    if (!row) return true;
    if (state.statuses.length && state.statuses.indexOf(row.dataset.pstatus) < 0) return false;
    if (state.pending && (row.dataset.pstatus === "done" || row.dataset.pstatus === "deferred")) return false;
    if (state.q && (row.dataset.psearch || "").indexOf(state.q) < 0) return false;
    return true;
  }
  function filterPartNode(el){
    if (!el || !el.classList) return true;
    if (el.classList.contains("prow-details")) {
      var summary = $(":scope > summary.prow", el);
      var childWrap = $(":scope > .fparts", el);
      var childVisible = false;
      if (childWrap) {
        Array.prototype.forEach.call(childWrap.children, function(c){
          if (filterPartNode(c)) childVisible = true;
        });
      }
      var visible = partOwnMatches(summary) || childVisible;
      el.hidden = !visible;
      if (visible && childVisible) el.open = true;
      return visible;
    }
    if (el.classList.contains("prow")) {
      var ok = partOwnMatches(el);
      el.hidden = !ok;
      return ok;
    }
    return true;
  }
  function anyPartFilterActive(){ return state.statuses.length > 0 || state.pending || !!state.q; }
  function applyTreeParts(){
    $$(".item-row").forEach(function(irow){
      var wrap = $(".fitems", irow);
      if (!wrap) return;
      var any = false;
      Array.prototype.forEach.call(wrap.children, function(node){
        if (filterPartNode(node)) any = true;
      });
      if (any && anyPartFilterActive() && !irow.hidden) irow.open = true;
    });
  }
  // A proposal shows how many of its items matched -- "3 of 16 items" --
  // next to its real done-count, which never moves: a filter narrows what
  // is shown, never what the numbers say is true. A proposal left with no
  // matching items is hidden entirely, and one that still has a match
  // opens on its own so the sponsor sees what matched without a second
  // click -- he is filtering in order to see the matches. It never closes
  // itself back while a filter is active, only Clear does that, so a
  // proposal the sponsor opened by hand is never fought.
  function applyFeatures(anyFilter){
    $$(".feature-row").forEach(function(frow){
      var rows2 = $$(".item-row", frow);
      var total = rows2.length, matched = 0;
      rows2.forEach(function(r){ if (!r.hidden) matched++; });
      var mEl = $(".fpmatched", frow);
      if (mEl) {
        mEl.hidden = !anyFilter;
        mEl.textContent = anyFilter ? matched + " of " + total + " items" : "";
      }
      frow.hidden = anyFilter && matched === 0;
      if (anyFilter && matched > 0) frow.open = true;
    });
  }
  function apply(){
    var shown = 0, total = 0, byStatus = {};
    // Count only the current view's own copy of an item -- Tree ("item-row"),
    // Kanban ("kcard"), Board ("card") or List ("row") -- never another
    // view's, even though every view carries [data-item] for the same
    // items. A bare tagName check (an <article> is both a card and a
    // kcard) double-counted a kcard into "#shown" and every status chip
    // whenever the Kanban view existed in the page, whether or not it was
    // the one shown (sponsor correction, 2026-09-18: these are the numbers
    // he reads to trust the page) -- the same rule now applies across all
    // four views, so switching views never changes a count.
    var counted = {tree: "item-row", kanban: "kcard", board: "card", list: "row"}[state.view] || "card";
    items.forEach(function(el){
      var ok = match(el, false, false);
      el.hidden = !ok;
      if (el.classList.contains(counted)) {
        total++;
        if (ok) shown++;
        // The chip count is the true count of each status among the other
        // filters (proposal/owner/tier/group/search) -- never zeroed out by
        // Pending or the show-finished toggle, or "Done" would misreport
        // as 0 (D4).
        if (match(el, true, true)) byStatus[el.dataset.status] = (byStatus[el.dataset.status] || 0) + 1;
      }
    });
    var anyFilter = !!(state.proposal || state.statuses.length || state.owner || state.tier
      || state.group || state.q || state.pending);
    applyTreeParts();
    applyFeatures(anyFilter);
    $$(".col,.kcol").forEach(function(col){
      var n = $$("[data-item]", col).filter(function(el){ return !el.hidden; }).length;
      $(".n", col).textContent = n;
      col.hidden = state.statuses.length > 0 && state.statuses.indexOf(col.dataset.column) < 0;
    });
    $$('.chip[data-filter="status"]').forEach(function(c){
      c.setAttribute("aria-pressed", state.statuses.indexOf(c.dataset.value) >= 0 ? "true" : "false");
      // Status chips are the canonical nested-task totals.  The filtered
      // copies below remain item-level controls, so they must not overwrite
      // the page's task denominator with top-level item counts.
      $(".n", c).textContent = c.dataset.taskCount || 0;
    });
    $$(".proposal").forEach(function(b){
      b.setAttribute("aria-pressed", b.dataset.proposal === state.proposal ? "true" : "false");
    });
    // The same "hide finished" rule (Pending, or Show finished off) governs
    // the Kanban done column: a "112 done -- show them" affordance stands
    // in for the cards until it's revealed, and Pending removes the
    // affordance itself -- there is no escape hatch back to done work
    // while Pending is on. The column itself and its real count never move
    // either way.
    var hideDone = hideFinished();
    $$('[data-kanban-done],[data-kanban-terminal]').forEach(function(kdone){ kdone.hidden = hideDone; });
    var kshow = $("[data-kanban-affordance]");
    if (kshow) { kshow.hidden = state.pending || !hideDone; }
    $$("[data-ask],[data-request]").forEach(function(el){
      var d = el.dataset;
      el.hidden = (!!state.proposal && d.proposal !== state.proposal) || (!!state.owner && d.owner !== state.owner)
        || (!!state.q && (d.search || "").indexOf(state.q) < 0);
    });
    var visible = function(list){ return list.filter(function(el){ return !el.hidden; }).length; };
    var attention = $("#attention");
    if (attention) {
      var waiting = visible($$("[data-ask],[data-request]", attention));
      $("#attention-n").textContent = waiting;
      attention.hidden = waiting === 0;
    }
    var answered = $("#answered");
    if (answered) {
      var done = visible($$("[data-ask]", answered));
      $("#answered-n").textContent = done;
      answered.hidden = done === 0;
    }
    $$("[data-view]").forEach(function(b){ b.setAttribute("aria-pressed", b.dataset.view === state.view ? "true" : "false"); });
    var t = $("#view-tree"); if (t) t.hidden = state.view !== "tree";
    var k = $("#view-kanban"); if (k) k.hidden = state.view !== "kanban";
    $("#board").hidden = state.view !== "board";
    $("#list").hidden = state.view !== "list";
    $("#none").hidden = shown > 0 || total === 0;
    var totalsPanel = $(".totals");
    var taskTotal = totalsPanel ? +(totalsPanel.dataset.taskTotal || total) : total;
    $("#shown").textContent = anyFilter ? shown + " of " + total + " items" : taskTotal + " tasks";
    $("#clear").hidden = !anyFilter;
  }
  var historyZoom = $("#history-zoom");
  if (historyZoom) historyZoom.addEventListener("change", function(ev){
    $$('[data-history-mode]').forEach(function(chart){ chart.hidden = chart.dataset.historyMode !== ev.target.value; });
  });
  function clear(){
    state.proposal = ""; state.statuses = []; state.owner = ""; state.tier = ""; state.group = ""; state.q = "";
    state.pending = false; state.showFinished = false;
    $("#q").value = ""; $("#owner").value = ""; $("#tier").value = ""; $("#group").value = "";
    var sf = $("#show-finished"); if (sf) { sf.checked = false; sf.disabled = false; }
    var pd = $("#pending"); if (pd) pd.checked = false;
    // Collapse the Proposals tree back to closed -- the auto-expand a
    // filter causes never survives Clear, even a row the sponsor opened
    // by hand while filtering.
    $$(".feature-row,.item-row,.prow-details").forEach(function(d){ d.open = false; });
    persist();
    apply();
  }
  $$(".proposal").forEach(function(b){ b.addEventListener("click", function(){
    state.proposal = state.proposal === b.dataset.proposal ? "" : b.dataset.proposal; persist(); apply(); }); });
  $$('.chip[data-filter="status"]').forEach(function(c){ c.addEventListener("click", function(){
    var i = state.statuses.indexOf(c.dataset.value);
    if (i >= 0) state.statuses.splice(i, 1); else state.statuses.push(c.dataset.value);
    persist(); apply(); }); });
  $("#owner").addEventListener("change", function(ev){ state.owner = ev.target.value; persist(); apply(); });
  $("#tier").addEventListener("change", function(ev){ state.tier = ev.target.value; persist(); apply(); });
  $("#group").addEventListener("change", function(ev){ state.group = ev.target.value; persist(); apply(); });
  var showFinished = $("#show-finished");
  if (showFinished) showFinished.addEventListener("change", function(ev){
    state.showFinished = ev.target.checked; persist(); apply(); });
  var pending = $("#pending");
  if (pending) pending.addEventListener("change", function(ev){
    state.pending = ev.target.checked;
    if (showFinished) { showFinished.disabled = state.pending; if (state.pending) showFinished.checked = false; }
    if (state.pending) state.showFinished = false;
    persist(); apply();
  });
  $$("[data-kanban-affordance]").forEach(function(b){ b.addEventListener("click", function(){
    if (state.pending) return;
    state.showFinished = true;
    if (showFinished) showFinished.checked = true;
    persist(); apply(); }); });
  $("#q").addEventListener("input", function(ev){ state.q = ev.target.value.trim().toLowerCase(); persist(); apply(); });
  $$("[data-view]").forEach(function(b){ b.addEventListener("click", function(){
    state.view = b.dataset.view; persist(); apply(); }); });
  $("#clear").addEventListener("click", clear);
  $("#clear2").addEventListener("click", clear);
  // proposal 30, P-13: "pull forward" copies the exact command that clears
  // one part's wait to the clipboard -- it never runs anything itself, so
  // the only job here is to get `data-cmd` onto the clipboard and reveal
  // the confirmation that already says so.
  function fallbackCopy(text){
    try {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.focus(); ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    } catch (e) {}
  }
  $$("[data-pull-forward-btn]").forEach(function(btn){
    btn.addEventListener("click", function(ev){
      ev.preventDefault();
      var wrap = btn.closest("[data-pull-forward]");
      if (!wrap) return;
      var cmd = wrap.getAttribute("data-cmd") || "";
      var confirmEl = $("[data-pull-forward-confirm]", wrap);
      function reveal(){ if (confirmEl) confirmEl.hidden = false; }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(cmd).then(reveal, function(){ fallbackCopy(cmd); reveal(); });
      } else {
        fallbackCopy(cmd); reveal();
      }
    });
  });
  // Sync the controls that carry their own value/checked state to what was
  // just restored from localStorage -- apply() below only sets aria-pressed
  // on buttons and chips, never a form control's own value.
  $("#q").value = state.q;
  $("#owner").value = state.owner;
  $("#tier").value = state.tier;
  $("#group").value = state.group;
  if (showFinished) { showFinished.checked = state.showFinished; showFinished.disabled = state.pending; }
  if (pending) pending.checked = state.pending;
  apply();
})();
