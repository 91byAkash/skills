<!-- Only needed once a repo has more than one glossary. One line per context, then how they talk. -->
# Glossary map

| Context | Glossary | Responsible for |
|---|---|---|
| Scheduling | [src/scheduling/GLOSSARY.md](./src/scheduling/GLOSSARY.md) | Slots, Holds and Appointments |
| Clinical records | [src/records/GLOSSARY.md](./src/records/GLOSSARY.md) | Visit notes and treatment plans |
| Invoicing | [src/invoicing/GLOSSARY.md](./src/invoicing/GLOSSARY.md) | Charges, insurer claims and receipts |

## How the contexts connect

- Scheduling → Clinical records: publishes `AppointmentAttended`; Records opens a visit note.
- Clinical records → Invoicing: publishes `VisitSigned`; Invoicing raises the charge.
- Scheduling and Invoicing share the `PatientRef` and `Price` types and nothing else.

## Words that change meaning at a boundary

- *Visit*: in Scheduling, the time booked; in Clinical records, the signed note. Convert explicitly when crossing.
