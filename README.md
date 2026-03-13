# Organ Donation Registry System

A Django-based hospital management system for tracking organ donors, recipients, and facilitating organ matching — featuring an **interactive human body organ map** on the dashboard.

## Quick Start

### Prerequisites

- Python 3.10+

### Setup & Run

```bash
# 1. Install Django
pip install django

# 2. Run database migrations
python manage.py migrate

# 3. (Optional) Load sample data
python manage.py shell -c "
from datetime import date
from registry.models import Donor, Recipient

Donor.objects.create(first_name='John', last_name='Doe', date_of_birth=date(1985, 3, 15), blood_type='O+', email='john@example.com', phone='555-0001', address='123 Main St', organs=['Heart', 'Kidney'], status='Active')
Donor.objects.create(first_name='Jane', last_name='Smith', date_of_birth=date(1990, 7, 22), blood_type='A+', email='jane@example.com', phone='555-0002', address='456 Oak Ave', organs=['Lungs', 'Corneas', 'Skin'], status='Active')
Recipient.objects.create(first_name='Alice', last_name='Brown', date_of_birth=date(1992, 1, 10), blood_type='O+', email='alice@example.com', phone='555-0004', address='321 Elm St', organ_needed='Heart', urgency='Critical', status='Active')
Recipient.objects.create(first_name='Charlie', last_name='Davis', date_of_birth=date(1988, 5, 20), blood_type='A+', email='charlie@example.com', phone='555-0005', address='654 Maple Ave', organ_needed='Kidney', urgency='High', status='Active')
print('Sample data created!')
"

# 4. Start the development server
python manage.py runserver
```

### View the Dashboard

Open your browser and go to: **http://127.0.0.1:8000/**

The **Interactive Organ Map** is displayed at the top of the dashboard homepage (`/`).

## Features

### Interactive Human Body Organ Map (Dashboard)

The dashboard features an SVG-based human body diagram where organs are color-coded based on donor/recipient availability:

| Color | Hex | Meaning |
|-------|-----|---------|
| Purple | `#a855f7` | Both donors and recipients available |
| Green | `#10B981` | Donors only |
| Red | `#EF4444` | Recipients only |
| Gray | `#94a3b8` | No activity |

**Interactions:**
- **Hover** over any organ on the body diagram to see a detail panel showing donor/recipient counts
- **Hover** over organ names in the side list to cross-highlight the organ on the body
- Active organs have a **pulsing glow** animation
- Organs are **keyboard-accessible** (Tab + focus)

### Other Features

- **Donor Management** — Register, view, edit, and delete organ donors (`/donors/`)
- **Recipient Management** — Register, view, edit, and delete organ recipients (`/recipients/`)
- **Organ Matching** — Manual and auto-matching of donors to recipients (`/matches/`)
- **Dashboard Charts** — Blood group distribution, organ availability, and recipient urgency charts
- **Admin Panel** — Django admin interface at `/admin/`

## Page Routes

| Page | URL |
|------|-----|
| Dashboard (with Organ Map) | `/` |
| All Donors | `/donors/` |
| Register Donor | `/donors/register/` |
| All Recipients | `/recipients/` |
| Register Recipient | `/recipients/register/` |
| All Matches | `/matches/` |
| Auto-Match | `/matches/auto/` |
| Create Match | `/matches/create/` |
| Admin Panel | `/admin/` |

## Running Tests

```bash
python manage.py test registry
```
