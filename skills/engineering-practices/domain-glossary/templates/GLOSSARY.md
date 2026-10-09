<!--
Glossary for one bounded context. Keep this header line and the entry shape below:
the term in bold followed by a colon, a definition of at most two sentences on the next
line, then an "_Avoid_:" line listing rejected synonyms (scripts/term-usage.sh reads it).
Optional extra line: "_Not to be confused with_: <other term> (<the difference>)".
-->
# Scheduling glossary

Scope: how patients get time with a practitioner, from offering availability to a completed visit. Code: `src/scheduling/`. Ask: <owner or channel>.

## Availability

**Slot**:
A span of a Practitioner's time that can be booked, published from their working pattern.
_Avoid_: opening, free time, availability block

**Hold**:
A Slot reserved for a few minutes while a patient finishes booking; it lapses on its own if not confirmed.
_Avoid_: lock, pending booking
_Not to be confused with_: Appointment (a Hold is not yet confirmed)

## Visits

**Appointment**:
A confirmed booking of one Slot by one patient for one service.
_Avoid_: booking, session, reservation

**No-show**:
An Appointment the patient neither attended nor cancelled before the cut-off.
_Avoid_: missed appointment, absence

## Retired terms

<!-- term → what replaced it and when, so old tickets and code stay readable -->
- *Session* → Appointment (renamed when group classes were introduced)
