(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.classList.add('js');

  /* ---- Light / dark toggle (remembered in this browser) ---- */
  var btn = document.getElementById('theme-toggle');
  function current() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function label() { btn.textContent = current() === 'dark' ? 'Light mode' : 'Dark mode'; }
  btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) { /* storage unavailable */ }
    label();
  });
  label();

  /* ---- Scroll progress bar ---- */
  var bar = document.getElementById('progress');
  var queued = false;
  function updateBar() {
    var max = root.scrollHeight - window.innerHeight;
    bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ')';
    queued = false;
  }
  window.addEventListener('scroll', function () {
    if (!queued) { queued = true; requestAnimationFrame(updateBar); }
  }, { passive: true });
  updateBar();

  /* ---- Highlight the nav link for the section in view ---- */
  if ('IntersectionObserver' in window) {
    var links = [].slice.call(document.querySelectorAll('nav a[href^="#"]'));
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.removeAttribute('aria-current'); });
        if (byId[e.target.id]) byId[e.target.id].setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(byId).forEach(function (id) {
      var s = document.getElementById(id);
      if (s) spy.observe(s);
    });
  }

  /* ---- Reveal content as it scrolls into view ---- */
  if (!reduce && 'IntersectionObserver' in window) {
    var items = [].slice.call(document.querySelectorAll('section > h2, .rows > .row, .rows > .empty, .skills > div'));
    items.forEach(function (el) {
      var i = [].indexOf.call(el.parentNode.children, el);
      el.style.transitionDelay = Math.min(i, 4) * 70 + 'ms';
      el.classList.add('reveal');
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---- Project category filter ---- */
  var filterPills = [].slice.call(document.querySelectorAll('.filter-pill'));
  var projectRows = [].slice.call(document.querySelectorAll('#project-rows .row'));
  if (filterPills.length && projectRows.length) {
    filterPills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        var filter = pill.getAttribute('data-filter');
        filterPills.forEach(function (p) {
          p.classList.remove('active');
          p.setAttribute('aria-pressed', 'false');
        });
        pill.classList.add('active');
        pill.setAttribute('aria-pressed', 'true');

        projectRows.forEach(function (row) {
          var cat = row.getAttribute('data-category');
          if (filter === 'all' || cat === filter) {
            row.classList.remove('filtered-out');
          } else {
            row.classList.add('filtered-out');
          }
        });
      });
    });
  }

  /* ---- Hero: a test run that types, ticks, and retries one flaky test ---- */
  var head = document.getElementById('report-head');
  var cmd = document.getElementById('report-cmd');
  var sum = document.getElementById('report-sum');
  var rows = [].slice.call(document.querySelectorAll('#report-rows li'));
  var flaky = document.querySelector('#report-rows li[data-flaky]');
  if (reduce || !cmd || !rows.length) return; // static final state is already in the HTML

  var text = cmd.textContent;
  var retry = flaky ? flaky.querySelector('.retry') : null;
  var finalSummary = sum.textContent;
  rows.forEach(function (r) { r.className = ''; });
  if (retry) retry.hidden = true;
  sum.textContent = 'running...';
  cmd.textContent = '';
  head.classList.add('typing');

  var c = 0;
  (function type() {
    if (c <= text.length) { cmd.textContent = text.slice(0, c++); setTimeout(type, 28); }
    else { head.classList.remove('typing'); setTimeout(next, 300); }
  })();

  var n = 0;
  function next() {
    if (n >= rows.length) { sum.textContent = finalSummary; return; }
    var row = rows[n];
    if (row === flaky) {
      row.className = 'fail';
      setTimeout(function () {
        row.className = 'ok';
        if (retry) retry.hidden = false;
        n++;
        setTimeout(next, 420);
      }, 800);
    } else {
      row.className = 'ok';
      n++;
      setTimeout(next, 420);
    }
  }
})();
