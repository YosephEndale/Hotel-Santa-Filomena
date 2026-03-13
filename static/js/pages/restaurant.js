/* ============================================================
   restaurant.js — Restaurant & Menu Page
   Hotel Santa Filomena
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Menu category tabs ────────────────────────────────
  const tabs   = document.querySelectorAll('.menu-nav__tab');
  const panels = document.querySelectorAll('.menu-panel');

  if (!tabs.length) return;

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      const target = this.dataset.category;

      // Deactivate all
      tabs.forEach(function (t)   { t.classList.remove('active'); });
      panels.forEach(function (p) { p.classList.remove('active'); });

      // Activate clicked tab and matching panel
      this.classList.add('active');
      const targetPanel = document.getElementById('panel-' + target);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });

  // Activate first tab on load
  if (tabs[0]) tabs[0].click();

});