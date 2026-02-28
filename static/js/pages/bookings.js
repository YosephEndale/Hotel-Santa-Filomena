/* ============================================================
   bookings.js — Booking Form Page
   Hotel Santa Filomena
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  const checkIn       = document.getElementById('id_check_in');
  const checkOut      = document.getElementById('id_check_out');
  const guestsInput   = document.getElementById('id_guests');
  const roomSelect    = document.getElementById('roomSelect');
  const summaryNights = document.getElementById('summaryNights');
  const summaryTotal  = document.getElementById('summaryTotal');
  const summaryGuests = document.getElementById('summaryGuests');
  const priceMeta     = document.getElementById('roomPriceMeta');

  // ── Set today as minimum check-in ─────────────────────
  const today   = new Date().toISOString().split('T')[0];
  if (checkIn)  checkIn.min  = today;
  if (checkOut) checkOut.min = today;

  // ── Enforce check-out after check-in ──────────────────
  if (checkIn) {
    checkIn.addEventListener('change', function () {
      if (checkOut) {
        checkOut.min = this.value;
        if (checkOut.value && checkOut.value <= this.value) {
          checkOut.value = '';
        }
      }
      updateSummary();
    });
  }

  if (checkOut) {
    checkOut.addEventListener('change', updateSummary);
  }

  if (guestsInput) {
    guestsInput.addEventListener('change', updateSummary);
  }

  // ── Update summary sidebar ─────────────────────────────
  function updateSummary() {
    if (!checkIn || !checkOut || !priceMeta) return;

    const price  = parseFloat(priceMeta.dataset.price || 0);
    const start  = new Date(checkIn.value);
    const end    = new Date(checkOut.value);
    const nights = Math.round((end - start) / (1000 * 60 * 60 * 24));

    if (nights > 0) {
      const total = nights * price;
      if (summaryNights) summaryNights.textContent = nights;
      if (summaryTotal)  summaryTotal.textContent  = '€' + total.toFixed(2);
      if (summaryGuests && guestsInput) {
        summaryGuests.textContent = guestsInput.value;
      }
    }
  }

  // Initial call in case dates are pre-filled
  updateSummary();

});