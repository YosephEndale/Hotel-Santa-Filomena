/* ============================================================
   room_detail.js — Room Detail Page
   Hotel Santa Filomena
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Lightbox ───────────────────────────────────────────
  const lightbox        = document.getElementById('lightbox');
  const lightboxImg     = document.getElementById('lightboxImg');
  const lightboxCounter = document.getElementById('lightboxCounter');

  let currentIndex  = 0;
  let galleryImages = [];

  // Collect image URLs from data attributes on gallery items
  document.querySelectorAll('.room-gallery__item').forEach(function (el) {
    galleryImages.push(el.dataset.src);
  });

  window.openLightbox = function (index) {
    if (!galleryImages.length) return;
    currentIndex = index;
    updateLightbox();
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
  };

  window.closeLightbox = function () {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
  };

  window.changeLightbox = function (direction) {
    currentIndex = (currentIndex + direction + galleryImages.length) % galleryImages.length;
    updateLightbox();
  };

  function updateLightbox() {
    lightboxImg.src = galleryImages[currentIndex];
    lightboxCounter.textContent = (currentIndex + 1) + ' / ' + galleryImages.length;
  }

  // Close on backdrop click
  if (lightbox) {
    lightbox.addEventListener('click', function (e) {
      if (e.target === this) window.closeLightbox();
    });
  }

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape')      window.closeLightbox();
    if (e.key === 'ArrowLeft')   window.changeLightbox(-1);
    if (e.key === 'ArrowRight')  window.changeLightbox(1);
  });

  // ── Price Calculator ───────────────────────────────────
  const checkIn       = document.getElementById('checkIn');
  const checkOut      = document.getElementById('checkOut');
  const summary       = document.getElementById('priceSummary');
  const nightCount    = document.getElementById('nightCount');
  const subtotalEl    = document.getElementById('subtotal');
  const totalPriceEl  = document.getElementById('totalPrice');
  const pricePerNight = parseFloat(
    document.getElementById('pricePerNight').dataset.price
  );

  function calculatePrice() {
    if (!checkIn.value || !checkOut.value) return;

    const start  = new Date(checkIn.value);
    const end    = new Date(checkOut.value);
    const nights = Math.round((end - start) / (1000 * 60 * 60 * 24));

    if (nights <= 0) {
      summary.style.display = 'none';
      return;
    }

    const total = nights * pricePerNight;
    nightCount.textContent   = nights;
    subtotalEl.textContent   = total.toFixed(2);
    totalPriceEl.textContent = total.toFixed(2);
    summary.style.display    = 'block';
  }

  if (checkIn && checkOut) {
    // Set min date to today
    const today  = new Date().toISOString().split('T')[0];
    checkIn.min  = today;
    checkOut.min = today;

    checkIn.addEventListener('change', function () {
      checkOut.min = this.value;
      if (checkOut.value && checkOut.value <= this.value) {
        checkOut.value        = '';
        summary.style.display = 'none';
      }
      calculatePrice();
    });

    checkOut.addEventListener('change', calculatePrice);
  }

});