/* ============================================================
   gallery.js — Gallery Page
   Hotel Santa Filomena
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Filter tabs ───────────────────────────────────────
  const filterBtns   = document.querySelectorAll('.gallery-filter-btn');
  const categories   = document.querySelectorAll('.gallery-category');

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = this.dataset.filter;

      // Update active tab
      filterBtns.forEach(function (b) { b.classList.remove('active'); });
      this.classList.add('active');

      // Show / hide categories
      categories.forEach(function (cat) {
        if (target === 'all' || cat.dataset.category === target) {
          cat.classList.remove('hidden');
        } else {
          cat.classList.add('hidden');
        }
      });
    });
  });

  // ── Lightbox ──────────────────────────────────────────
  const lightbox     = document.getElementById('lightbox');
  const lbImg        = document.getElementById('lbImg');
  const lbCaption    = document.getElementById('lbCaption');
  const lbClose      = document.getElementById('lbClose');
  const lbPrev       = document.getElementById('lbPrev');
  const lbNext       = document.getElementById('lbNext');
  const lbCounter    = document.getElementById('lbCounter');

  let allImages = [];   // {src, caption}
  let currentIdx = 0;

  // Collect all gallery items on page
  function buildImageList() {
    allImages = [];
    document.querySelectorAll('.gallery-img-trigger').forEach(function (el) {
      allImages.push({
        src:     el.dataset.src,
        caption: el.dataset.caption || '',
      });
    });
  }

  function openLightbox(idx) {
    buildImageList();
    currentIdx = idx;
    showImage(currentIdx);
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
  }

  function showImage(idx) {
    if (!allImages.length) return;
    const item    = allImages[idx];
    lbImg.src     = item.src;
    lbCaption.textContent = item.caption;
    lbCounter.textContent = (idx + 1) + ' / ' + allImages.length;
  }

  function prevImage() {
    currentIdx = (currentIdx - 1 + allImages.length) % allImages.length;
    showImage(currentIdx);
  }

  function nextImage() {
    currentIdx = (currentIdx + 1) % allImages.length;
    showImage(currentIdx);
  }

  // Click on any gallery item
  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.gallery-img-trigger');
    if (!trigger) return;
    buildImageList();
    const idx = Array.from(
      document.querySelectorAll('.gallery-img-trigger')
    ).indexOf(trigger);
    openLightbox(idx);
  });

  if (lbClose)  lbClose.addEventListener('click', closeLightbox);
  if (lbPrev)   lbPrev.addEventListener('click',  prevImage);
  if (lbNext)   lbNext.addEventListener('click',  nextImage);

  // Click outside image to close
  lightbox && lightbox.addEventListener('click', function (e) {
    if (e.target === lightbox) closeLightbox();
  });

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (!lightbox || !lightbox.classList.contains('open')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowLeft')  prevImage();
    if (e.key === 'ArrowRight') nextImage();
  });

});