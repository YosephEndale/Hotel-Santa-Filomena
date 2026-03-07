/* ============================================================
   table_booking.js — Table Booking Form
   Hotel Santa Filomena
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  const dateInput   = document.getElementById('id_date');
  const timeSelect  = document.getElementById('id_time_slot');
  const serviceLabel = document.getElementById('serviceLabel');

  // ── Set min date to today ──────────────────────────────
  if (dateInput) {
    const today    = new Date().toISOString().split('T')[0];
    dateInput.min  = today;

    dateInput.addEventListener('change', function () {
      validateDay(this.value);
      updateSummary();
    });
  }

  // ── Block Mondays ──────────────────────────────────────
  function validateDay(dateValue) {
    if (!dateValue) return;
    const day     = new Date(dateValue).getDay();
    const warning = document.getElementById('mondayWarning');
    // getDay() returns 1 for Monday
    if (day === 1) {
      if (warning) warning.style.display = 'block';
      if (dateInput) dateInput.value = '';
    } else {
      if (warning) warning.style.display = 'none';
    }
  }

  // ── Update service label (Pranzo / Cena) ──────────────
  if (timeSelect) {
    timeSelect.addEventListener('change', function () {
      updateServiceLabel(this.value);
      updateSummary();
    });
    // Run on load in case of pre-filled value
    updateServiceLabel(timeSelect.value);
  }

  function updateServiceLabel(timeValue) {
    if (!serviceLabel) return;
    if (!timeValue) return;
    const hour = parseInt(timeValue.split(':')[0], 10);
    serviceLabel.textContent = hour < 16 ? 'Pranzo' : 'Cena';
  }

  // ── Update summary sidebar ─────────────────────────────
  function updateSummary() {
    const summaryDate     = document.getElementById('summaryDate');
    const summaryTime     = document.getElementById('summaryTime');
    const summaryService  = document.getElementById('summaryService');
    const summaryGuests   = document.getElementById('summaryGuests');
    const guestsInput     = document.getElementById('id_guests');

    if (summaryDate && dateInput && dateInput.value) {
      const d = new Date(dateInput.value);
      summaryDate.textContent = d.toLocaleDateString('it-IT', {
        weekday: 'long',
        year:    'numeric',
        month:   'long',
        day:     'numeric',
      });
    }
    if (summaryTime && timeSelect && timeSelect.value) {
      summaryTime.textContent = timeSelect.value;
    }
    if (summaryService && serviceLabel) {
      summaryService.textContent = serviceLabel.textContent;
    }
    if (summaryGuests && guestsInput) {
      summaryGuests.textContent = guestsInput.value;
    }
  }

  // Update guests count live
  const guestsInput = document.getElementById('id_guests');
  if (guestsInput) {
    guestsInput.addEventListener('change', updateSummary);
    guestsInput.addEventListener('input', updateSummary);
  }

  // Initial summary update
  updateSummary();

});