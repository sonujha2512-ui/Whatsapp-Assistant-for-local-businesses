import re
from datetime import datetime
import database

# date formats the user might type in
date_fmts = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']

time_regex = re.compile(r'^\d{1,2}:\d{2}\s?(AM|PM|am|pm)?$')

# we only do bookings from 9am to 5pm, on the hour
slots = []
for h in range(9, 18):
    slots.append(str(h).zfill(2) + ':00')


def parse_date(txt):
    txt = txt.strip()
    for fmt in date_fmts:
        try:
            dt = datetime.strptime(txt, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


def parse_time(txt):
    txt = txt.strip().upper().replace(' ', '')
    if not time_regex.match(txt):
        return None

    # try to figure out what they meant
    try:
        if 'AM' in txt or 'PM' in txt:
            if ':' in txt:
                dt = datetime.strptime(txt, '%I:%M%p')
            else:
                dt = datetime.strptime(txt, '%I%p')
        else:
            dt = datetime.strptime(txt, '%H:%M')
        return dt.strftime('%H:%M')
    except ValueError:
        return None


def create_booking(phone, name, date_str, time_str):
    d = parse_date(date_str)
    if d is None:
        return False, "I couldn't understand that date. Try format YYYY-MM-DD (e.g. 2026-10-05)."

    t = parse_time(time_str)
    if t is None:
        return False, "I couldn't understand that time. Try e.g. 14:00 or 2:00PM."

    if t not in slots:
        return False, "That slot isn't available. We book on the hour between " + slots[0] + " and " + slots[-1] + "."

    if database.is_slot_taken(d, t):
        return False, "Sorry, " + d + " at " + t + " is already booked. Pick another time."

    bid = database.add_booking(phone, name, d, t)
    return True, "Booked! Confirmation #" + str(bid) + " — " + d + " at " + t + "."


def list_bookings(phone):
    bks = database.get_bookings_for_phone(phone)
    if len(bks) == 0:
        return "You have no upcoming bookings."
    lines = []
    for b in bks:
        lines.append('#' + str(b['id']) + ': ' + b['date'] + ' at ' + b['time'])
    return "Your bookings:\n" + "\n".join(lines)


def cancel(phone, id_str):
    try:
        bid = int(id_str.strip().lstrip('#'))
    except ValueError:
        return "Give me the booking number to cancel, e.g. 'cancel 3'."

    ok = database.cancel_booking(bid, phone)
    if ok:
        return "Booking #" + str(bid) + " cancelled."
    return "Couldn't find booking #" + str(bid) + " under your number."