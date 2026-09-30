(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const layout = document.getElementById('seatLayout');
        if (!layout) return;

        const SEATS = window.__SEAT_BOARD__ || [];
        const STYLE = window.__SEAT_STYLE__ || 'seater';
        const IS_SLEEPER = !!window.__IS_SLEEPER__;

        const selected = new Set();
        const MAX_SEATS = 6;

        // Layout topology: columns [1, 2] | aisle (3) | [4, 5]
        const IS_RIGHT = { 1: false, 2: false, 4: true, 5: true };

        // ---- Build the board ------------------------------------------------
        function positionLabel(seat) {
            if (seat.window) return 'Window';
            return 'Aisle';
        }

        function seatCard(seat) {
            const state = seat.booked ? 'booked' : 'available';
            const extra = seat.window ? ' window' : '';
            const deckLabel = seat.deck === 2 ? '(Upper)' : '(Lower)';
            const tooltip = `${seat.num} · ${positionLabel(seat)} · ₹${seat.price}` +
                (IS_SLEEPER ? ` ${deckLabel}` : '') +
                (seat.booked ? ' · Booked' : ' · Available');
            return `<button type="button" class="seat-btn ${state}${extra}" data-id="${seat.id}" data-price="${seat.price}" title="${tooltip}" aria-pressed="false">
                        <span class="seat-num">${seat.num}</span>
                        <span class="seat-price">₹${seat.price}</span>
                    </button>`;
        }

        function renderSeats() {
            if (!SEATS.length) {
                layout.innerHTML = '<p class="text-muted" style="text-align:center;padding:2rem;">No seats available on this bus.</p>';
                return;
            }

            // Group seats by deck then by row, preserving column order
            const decks = {};
            SEATS.forEach(s => {
                if (!decks[s.deck]) decks[s.deck] = {};
                if (!decks[s.deck][s.row]) decks[s.deck][s.row] = [];
                decks[s.deck][s.row].push(s);
            });

            let html = '<div class="bus-frame">';
            html += '<div class="bus-driver"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="9" opacity="0.9"/><circle cx="12" cy="12" r="3.5"/></svg><span>DRIVER</span></div>';

            Object.keys(decks).sort((a, b) => a - b).forEach(deckNum => {
                const rows = decks[deckNum];
                const deckTitle = IS_SLEEPER
                    ? (deckNum === '2' ? 'Upper Deck' : 'Lower Deck')
                    : (STYLE === 'premium' ? 'Premium Cabin' : 'Main Cabin');

                html += `<div class="bus-deck-block"><div class="deck-head"><span class="deck-name">${deckTitle}</span><span class="deck-rule"></span></div><div class="bus-deck">`;

                Object.keys(rows).sort((a, b) => a - b).forEach(rowNum => {
                    const rowSeats = rows[rowNum].slice().sort((a, b) => a.col - b.col);
                    const left = rowSeats.filter(s => IS_RIGHT[s.col] === false);
                    const right = rowSeats.filter(s => IS_RIGHT[s.col] === true);

                    html += '<div class="seat-row">';
                    html += `<span class="row-label">${rowNum}</span>`;
                    left.forEach(s => { html += seatCard(s); });
                    html += '<span class="seat-aisle"></span>';
                    right.forEach(s => { html += seatCard(s); });
                    html += '</div>';
                });
                html += '</div></div>';
            });

            html += '<div class="bus-rear"><span>REAR</span></div>';
            html += '</div>';

            layout.innerHTML = html;

            layout.querySelectorAll('.seat-btn.available').forEach(btn => {
                btn.addEventListener('click', function () {
                    toggleSeat(this);
                });
            });
            updateSummary();
        }

        // ---- Selection logic ------------------------------------------------
        function toggleSeat(btn) {
            const id = btn.dataset.id;
            if (selected.has(id)) {
                selected.delete(id);
                btn.classList.remove('selected');
                btn.setAttribute('aria-pressed', 'false');
            } else {
                if (selected.size >= MAX_SEATS) {
                    alert('You can select a maximum of ' + MAX_SEATS + ' seats.');
                    return;
                }
                selected.add(id);
                btn.classList.add('selected');
                btn.setAttribute('aria-pressed', 'true');
            }
            updateSummary();
        }

        function seatInfo(id) {
            for (const s of SEATS) {
                if (String(s.id) === String(id)) return s;
            }
            return null;
        }

        function updateSummary() {
            const listEl = document.getElementById('selectedSeats');
            const emptyEl = document.getElementById('selectedEmpty');
            const baseEl = document.getElementById('baseFare');
            const countEl = document.getElementById('seatCount');
            const totalEl = document.getElementById('totalFare');
            const btn = document.getElementById('proceedBtn');
            const input = document.getElementById('seatIdsInput');

            if (selected.size === 0) {
                if (emptyEl) emptyEl.style.display = '';
                listEl.innerHTML = '';
                baseEl.textContent = '₹0';
                countEl.textContent = '0';
                totalEl.textContent = '₹0';
                btn.disabled = true;
                input.value = '';
                return;
            }

            if (emptyEl) emptyEl.style.display = 'none';

            let total = 0;
            let rowsHtml = '';
            selected.forEach(id => {
                const s = seatInfo(id);
                if (!s) return;
                total += parseFloat(s.price);
                const tag = s.window ? '<span class="seat-pos-tag win">W</span>' : '<span class="seat-pos-tag aisle">A</span>';
                rowsHtml += `<div class="sel-row">
                    <span class="sel-label">${tag} ${s.num}</span>
                    <span class="sel-price">₹${s.price}</span>
                </div>`;
            });

            listEl.innerHTML = rowsHtml;
            baseEl.textContent = '₹' + total.toFixed(2);
            countEl.textContent = selected.size + (selected.size > 1 ? ' seats' : ' seat');
            totalEl.textContent = '₹' + total.toFixed(2);
            btn.disabled = false;
            input.value = Array.from(selected).join(',');
        }

        renderSeats();
    });
})();