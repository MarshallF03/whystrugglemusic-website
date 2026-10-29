// Why Struggle Music website script. The site works without it.
//
// Search and topic filter for the music business hub: every guide is listed
// without this file. With it, the list
// narrows as you type or pick a topic, and a status message tells screen
// reader users how many guides match. The address bar keeps ?q= and
// ?category= up to date, so a filtered list can be shared as a link.
// Release countdowns: keeps "N days, N hours and N minutes to go" up to date.
// It is deliberately not a live region, so screen readers are never
// interrupted; reading the line gives the current count.
(function () {
  "use strict";

  var els = document.querySelectorAll("[data-countdown]");
  if (els.length === 0) { return; }

  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }

  function update() {
    var now = new Date();
    for (var i = 0; i < els.length; i++) {
      var p = els[i].getAttribute("data-countdown").split("-");
      var release = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
      var minutes = Math.floor((release - now) / 60000);
      var text;
      if (minutes <= 0) {
        text = (now - release) < 86400000 ? "It is out today!" : "It is out now.";
      } else {
        var days = Math.floor(minutes / 1440);
        var hours = Math.floor((minutes % 1440) / 60);
        var mins = minutes % 60;
        var parts = [];
        if (days) { parts.push(plural(days, "day")); }
        if (hours) { parts.push(plural(hours, "hour")); }
        parts.push(plural(mins, "minute"));
        text = (parts.length > 1 ? parts.slice(0, -1).join(", ") + " and " + parts[parts.length - 1] : parts[0]) + " to go.";
      }
      els[i].textContent = text;
    }
  }
  update();
  setInterval(update, 60000);
})();

(function () {
  "use strict";

  var form = document.querySelector("form.search");
  var list = document.getElementById("articles");
  var status = document.getElementById("results-status");
  if (!form || !list || !status) { return; }

  var input = document.getElementById("q");
  var select = document.getElementById("category");
  var items = [].slice.call(list.querySelectorAll("li.article"));
  if (items.length === 0) { return; }

  var categories = [].slice.call(select.options).map(function (o) { return o.value; });

  function words(text) {
    // "PRS's" finds PRS guides: a trailing 's (straight or curly apostrophe) is ignored.
    return text.toLowerCase().trim().split(/\s+/)
      .map(function (w) { return w.replace(/['’]s$/, ""); })
      .filter(Boolean);
  }

  function topicName() {
    return select.value ? select.options[select.selectedIndex].text : "";
  }

  function apply(announce) {
    var query = words(input.value);
    var category = select.value;
    var shown = 0;
    items.forEach(function (li) {
      var haystack = li.getAttribute("data-search");
      var match = (!category || li.getAttribute("data-category") === category) &&
        query.every(function (w) { return haystack.indexOf(w) !== -1; });
      li.hidden = !match;
      if (match) { shown += 1; }
    });
    list.hidden = shown === 0;

    var message;
    var filtered = query.length > 0 || category;
    if (!filtered) {
      message = "Showing all " + items.length + (items.length === 1 ? " guide." : " guides.");
    } else if (shown === 0) {
      message = "No guides match";
      if (query.length) { message += " “" + input.value.trim() + "”"; }
      if (category) { message += " in " + topicName(); }
      message += (/[.!?]$/.test(message) ? "" : ".") + " Try a different word or choose All topics.";
    } else {
      message = "Showing " + shown + " of " + items.length + " guides";
      if (query.length) { message += " matching “" + input.value.trim() + "”"; }
      if (category) { message += " in " + topicName(); }
      if (!/[.!?]$/.test(message)) { message += "."; }
    }
    // textContent, never innerHTML: the search words are never treated as code.
    if (announce) { status.textContent = message; }

    var params = new URLSearchParams();
    if (input.value.trim()) { params.set("q", input.value.trim()); }
    if (category) { params.set("category", category); }
    var qs = params.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
  }

  // Start from the address bar, ignoring a topic that does not exist.
  var start = new URLSearchParams(location.search);
  input.value = start.get("q") || "";
  var startCategory = start.get("category") || "";
  select.value = categories.indexOf(startCategory) !== -1 ? startCategory : "";
  apply(Boolean(input.value || select.value));

  var timer;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { apply(true); }, 300);
  });
  select.addEventListener("change", function () { apply(true); });
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    clearTimeout(timer);
    apply(true);
  });
})();
