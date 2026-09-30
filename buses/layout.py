"""Real bus seat layout engine.

Every seat is a row in the Seat table keyed to its Bus (never HTML).

Layout styles (chosen from the bus type):
  seater   -> 2+2 rows, A1..A{N} sequential numbering
  sleeper  -> lower berths (deck 1, L#) and upper berths (deck 2, U#)
  premium  -> luxury / volvo seater, 01..N sequential numbering

All rows share the aisle topology of the physical bus:
  columns 1,2  |  3 (aisle)  |  4,5
  window = col 1 or 5, aisle = col 2 or 4
"""
from __future__ import annotations

from decimal import Decimal


def layout_style(bus) -> str:
    """Return 'seater' | 'sleeper' | 'premium' for a Bus or BusType."""
    bt = getattr(bus, 'bus_type', None) or bus
    is_sleeper = getattr(bt, 'is_sleeper', False)
    name = getattr(bt, 'name', '') or ''
    if is_sleeper:
        return 'sleeper'
    lower = name.lower()
    if 'volvo' in lower or 'luxury' in lower:
        return 'premium'
    return 'seater'


def seat_specs(bus) -> list:
    """Build a deterministic list of seat attribute dicts for a bus.

    Returns exactly ``bus.total_seats`` specs: each dict carries
    seat_number, seat_type, deck, row, column, is_window, price_multiplier.
    """
    style = layout_style(bus)
    total = int(bus.total_seats)
    specs: list = []

    if style == 'sleeper':
        rows = (total + 3) // 4        # 4 berths per vertical pair row
        lc = uc = 0                    # lower / upper counters
        for r in range(1, rows + 1):
            for side, (col, deck, counter) in enumerate([
                (1, 1, 'L'), (2, 1, 'L'), (4, 2, 'U'), (5, 2, 'U'),
            ]):
                if len(specs) >= total:
                    break
                counter_key = counter
                n = lc + 1 if counter_key == 'L' else uc + 1
                if counter_key == 'L':
                    lc += 1
                else:
                    uc += 1
                specs.append({
                    'seat_number': f'{counter_key}{n}',
                    'seat_type': 'sleeper',
                    'deck': deck,
                    'row': r,
                    'column': col,
                    'is_window': col in (1, 5),
                    'price_multiplier': Decimal('1.10') if (col in (1, 5) and deck == 1)
                                        else Decimal('1.05') if (col not in (1, 5) and deck == 1)
                                        else Decimal('1.00') if (col in (1, 5))
                                        else Decimal('0.95'),
                })
        return specs

    # 2+2 seater / premium: columns 1,2 | aisle(3) | 4,5, seq numbering across the bus
    seq = 0
    rows = (total + 3) // 4
    for r in range(1, rows + 1):
        for col in (1, 2, 4, 5):
            if len(specs) >= total:
                break
            seq += 1
            base = Decimal('1.08') if style == 'premium' and col in (1, 5) else Decimal('1.00')
            if style == 'seater' and col not in (1, 5):
                base = Decimal('1.00')
            if style == 'seater' and col in (1, 5):
                base = Decimal('1.05')
            specs.append({
                'seat_number': f'{seq:02d}' if style == 'premium' else f'A{seq:02d}',
                'seat_type': 'seater',
                'deck': 1,
                'row': r,
                'column': col,
                'is_window': col in (1, 5),
                'price_multiplier': base,
            })
    return specs


def apply_layout(bus, create_only: bool = False) -> tuple:
    """Synchronise the Seat rows of ``bus`` to the real layout.

    Preserves existing Seat row IDs (so BookingSeat references stay valid):
    rows are re-numbered via a temp pass, then assigned final attributes.
    When ``create_only`` is True, only missing seats are added (no updates).

    Returns (created, updated).
    """
    from .models import Seat

    specs = seat_specs(bus)
    existing = list(Seat.objects.filter(bus=bus).order_by('id'))
    created = updated = 0

    if create_only:
        taken = {s.seat_number for s in existing}
        for spec in specs:
            if spec['seat_number'] in taken:
                continue
            Seat.objects.create(bus=bus, **spec)
            created += 1
        return created, 0

    # Phase 1: temp unique numbers to avoid unique_together collisions
    for i, seat in enumerate(existing):
        seat.seat_number = f'X{i:04d}'
        Seat.objects.filter(pk=seat.pk).update(seat_number=seat.seat_number)

    # Phase 2: assign final layout
    for seat, spec in zip(existing, specs):
        seat.seat_number = spec['seat_number']
        seat.seat_type = spec['seat_type']
        seat.deck = spec['deck']
        seat.row = spec['row']
        seat.column = spec['column']
        seat.is_window = spec['is_window']
        seat.price_multiplier = spec['price_multiplier']
        seat.save(update_fields=['seat_number', 'seat_type', 'deck', 'row', 'column',
                                 'is_window', 'price_multiplier'])
        updated += 1

    # extra rows beyond total (shouldn't happen, but be safe)
    for seat in existing[len(specs):]:
        seat.delete()

    # record layout metadata on the bus for previews
    style = layout_style(bus)
    bus.seat_layout = {
        'style': style,
        'cols': [1, 2, 4, 5],
        'aisle_col': 3,
        'rows': (len(specs) + 3) // 4,
        'total': len(specs),
    }
    bus.save(update_fields=['seat_layout'])
    return created, updated