# GoBus - Bus Booking System

A comprehensive bus booking platform built with Django, featuring passenger, agency, and admin modules.

## Features

### Passenger Module
- Search and book bus tickets
- Seat selection with real-time availability
- Multiple payment methods (UPI, Card, Wallet)
- Live bus tracking
- Wallet and referral system
- AI assistant for queries
- Reviews and ratings

### Agency Module
- Manage buses, routes, and schedules
- View bookings and passenger details
- Track earnings and analytics
- Respond to reviews

### Admin Module
- Manage users (passengers & agencies)
- Approve/reject agencies
- System-wide analytics and reports
- Manage buses, routes, and bookings

## Tech Stack

- **Backend:** Django 4.2+
- **Database:** PostgreSQL
- **Real-time:** Django Channels + Redis
- **Frontend:** Bootstrap 5, Font Awesome
- **Forms:** Django Crispy Forms

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GoBus.git
cd GoBus
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```sql
CREATE DATABASE gobus_db;
```

5. Configure `.env` file with your database credentials

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
GoBus/
├── manage.py
├── requirements.txt
├── .env
├── GoBus/           # Project settings
├── accounts/        # User authentication
├── passengers/      # Passenger features
├── agencies/        # Agency management
├── buses/           # Bus management
├── routes/          # Route management
├── schedules/       # Schedule management
├── bookings/        # Booking system
├── payments/        # Payment processing
├── cancellations/   # Cancellation handling
├── tracking/        # Live bus tracking
├── reviews/         # Reviews & ratings
├── notifications/   # In-app notifications
├── wallets/         # Wallet system
├── referrals/       # Referral program
├── ai_assistant/    # AI chatbot
├── templates/       # HTML templates
├── static/          # CSS, JS, images
├── media/           # User uploads
└── tests/           # Test files
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | - |
| DEBUG | Debug mode | True |
| DB_NAME | PostgreSQL database name | gobus_db |
| DB_USER | Database user | postgres |
| DB_PASSWORD | Database password | postgres |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |

## License

MIT License
