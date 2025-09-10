
# DCTFd - Capture The Flag Platform

<p align="center">
  <img src="static/images/logo.png" alt="DCTFd Logo" width="150">
</p>

Hey there! Welcome to DCTFd, a Django-powered platform for running awesome Capture The Flag competitions.

Developed by Srivatsan Sk | Copyright (c) 2025 | MIT License

## What's this all about?

DCTFd started as a personal project to solve a problem: I needed a flexible, modern platform for hosting CTF events with more advanced user role management. The main motivation was creating a platform with distinct user roles (participants, organizers, administrators) and better extensibility. So I built DCTFd - a Django implementation inspired by the popular CTFd platform but with significant improvements to user management and platform architecture.

This platform lets you run cybersecurity competitions where participants tackle various challenges - from cryptography puzzles to web exploits - earning points and competing on a leaderboard. It's designed to be straightforward enough for classroom use but powerful enough for large-scale competitions.

Some cool things DCTFd can do:
- Host a variety of challenge types (standard, dynamic scoring, etc.)
- Manage teams and users with granular permission levels (the primary reason for creating DCTFd!)
- Leverage Django's app-based architecture for better extensibility and customization
- Track scores in real-time with live leaderboards
- Customize the look and feel to match your event
- Scale from small classroom exercises to large competitions

I've built this with a focus on making both the participant experience and the organizer experience as smooth as possible. No unnecessary complexity, just the features you need to run a great CTF.

Want to help out? Awesome! Check out our [contribution guidelines](CONTRIBUTING.md) - we welcome all kinds of help, whether you're fixing bugs, adding features, or improving documentation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup](#docker-setup)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [Usage](#usage)
  - [Setting Up Your First Event](#setting-up-your-first-event)
  - [Challenge Management](#challenge-management)
  - [Team Management](#team-management)
  - [User Management](#user-management)
- [Development](#development)
  - [Code Structure](#code-structure)
  - [Database Migrations](#database-migrations)
  - [Avatar System](#avatar-system)
  - [Custom Features](#custom-features)
- [Deployment](#deployment)
  - [Production Considerations](#production-considerations)
  - [Security Checklist](#security-checklist)
- [Contributing](#contributing)
- [License](#license)

## Overview

DCTFd is a Django-based implementation of a CTF platform inspired by CTFd. It provides a complete solution for hosting cybersecurity competitions with features for challenge management, team formation, scoring, and event administration. The primary advantage of DCTFd is its advanced user role system and Django-based extensibility, making it perfect for organizations that need more control over user permissions and platform customization.

## Features

- **Multi-user Roles**: Sophisticated role management with distinct capabilities for participants, organizers, and administrators - the main reason DCTFd was created!
- **Extensible Architecture**: Built on Django's app-based system for easy customization and addition of new features
- **Team Management**: Create teams, manage members, and track team progress
- **Challenge System**: Multiple challenge types, categories, and dynamic scoring
- **Event Management**: Configure competition parameters, start/end times, and access controls
- **Scoring System**: Real-time scoring, leaderboards, and score history
- **User Profiles**: Customizable profiles with avatar selection
- **Admin Tools**: Comprehensive dashboards for event management and analytics
- **Responsive Design**: Mobile-friendly interface for all users

## System Requirements

- Python 3.9+
- Django 4.2+
- PostgreSQL (recommended for production) or SQLite (development)
- Redis (for caching and session storage)
- Nginx (for production deployment)

## Installation

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sr1v47s4n/DCTFd.git
   cd DCTFd
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate a secret key**:
   ```bash
   python generate_secret_key.py
   ```

5. **Set up environment variables** - Create a `.env` file in the project root with the following mandatory fields:
   ```
   # Required settings
   DEBUG=True
   SECRET_KEY=your-generated-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1
   DEV_MODE=True
   
   # Database (choose one option)
   # Option 1: SQLite for development
   DATABASE_URL=sqlite:///db.sqlite3
   # Option 2: PostgreSQL (uncomment and edit)
   # DATABASE_URL=postgresql://dctfd_user:password@localhost:5432/dctfd_db
   
   # Event settings
   EVENT_NAME=Development CTF
   
   # Email settings (optional for development)
   # EMAIL_HOST=smtp.gmail.com
   # EMAIL_PORT=587
   # EMAIL_USE_TLS=True
   # EMAIL_HOST_USER=your-email@gmail.com
   # EMAIL_HOST_PASSWORD=your-app-password
   # DEFAULT_FROM_EMAIL=noreply@dctfd.com
   ```

6. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

7. **Load avatar data** (optional):
   ```bash
   python load_avatars.py
   ```

8. **Enable development mode** (optional):
   ```bash
   python manage.py devmode on
   ```

9. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

10. **Access the application**:
    ```
    http://localhost:8000/
    ```

### Docker Setup

> **Coming Soon!** Docker support for DCTFd is currently under development. The complete Docker implementation with PostgreSQL, Redis, and Nginx integration will be available in an upcoming release. Stay tuned for containerized deployment options that will make running DCTFd in production environments much easier.

In the meantime, please use the [Local Development Setup](#local-development-setup) instructions to get started with DCTFd.

## Configuration

### Environment Variables

DCTFd uses environment variables for configuration, which can be set in a `.env` file at the project root. This file is automatically loaded by the application at startup.

#### Creating the .env File

1. Create a file named `.env` in the root directory of the project
2. Add key-value pairs in the format `KEY=VALUE`, one per line
3. Do not use quotes around values unless they are part of the value
4. Do not include spaces around the equals sign

#### Required Variables

At a minimum, your `.env` file should include:

```
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Complete Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEBUG` | Enable/disable debug mode | `True` in dev, `False` in prod | `DEBUG=False` |
| `SECRET_KEY` | Django secret key | Auto-generated in dev | `SECRET_KEY=your-secure-secret-key` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` in dev | `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com` |
| `DEV_MODE` | Enable/disable development mode | `True` in dev, `False` in prod | `DEV_MODE=False` |
| `EVENT_NAME` | Default event name | `DCTFd CTF` | `EVENT_NAME=My Awesome CTF` |

#### Database Configuration

You can configure the database in two ways:

1. **Using DATABASE_URL** (recommended for production):
   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database_name
   ```

2. **Using individual database settings**:
   ```
   DB_NAME=dctfd_db
   DB_USER=dctfd_user
   DB_PASSWORD=securepassword
   DB_HOST=localhost
   DB_PORT=5432
   ```

The `DATABASE_URL` format follows this pattern:
- SQLite: `sqlite:///path/to/db.sqlite3`
- PostgreSQL: `postgresql://user:password@hostname:port/database`
- MySQL: `mysql://user:password@hostname:port/database`

#### Email Configuration

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

#### Cloud Storage Configuration (Optional)

For production environments, you may want to use cloud storage for user uploads:

```
USE_CLOUD_STORAGE=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

#### Example .env File for Development

```
DEBUG=True
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DEV_MODE=True
DATABASE_URL=sqlite:///db.sqlite3
EVENT_NAME=Development CTF
```

#### Example .env File for Production

```
DEBUG=False
DEV_MODE=False
SECRET_KEY=your-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://dctfd_user:securepassword@localhost:5432/dctfd_db
EVENT_NAME=Production CTF
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SECURE_SSL_REDIRECT=True
```

### Development Mode

Development mode automatically sets up a pre-configured CTF environment with sample data:

```bash
# Enable development mode
python manage.py devmode on

# Disable development mode
python manage.py devmode off
```

**Development Mode Features**:
- Default admin user (username: `admin`, password: `admin`)
- Sample event with reasonable settings
- Sample challenges and categories
- Test team
- Visual indicator that you're in development mode

**Security Warning**: Development mode uses simplified settings and credentials that are **NOT SECURE** for production use.

### Production Mode

For production deployment, set the following minimum configuration:

```
DEBUG=False
DEV_MODE=False
SECRET_KEY=your-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/dctfd_prod
```

## Usage

### Setting Up Your First Event

1. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Start the server**:
   ```bash
   python manage.py runserver
   ```

3. **Navigate to the event setup page**:
   ```
   http://localhost:8000/event/setup/
   ```

4. **Fill out the setup form** with your event details:
   - Event name, description, and format
   - Time settings (start/end times, registration period)
   - Root admin account credentials
   - Appearance settings (theme, colors, logo, banner)
   - Advanced settings

5. **Review and confirm** your settings on the confirmation page.

6. **Click "Confirm and Create"** to complete the setup.

7. **Log in** with your newly created admin account.

### Challenge Management

1. **Access the admin dashboard** after logging in as an organizer or admin.

2. **Navigate to Challenges** in the admin menu.

3. **Create challenge categories** by clicking "Add Category".

4. **Add challenges** by clicking "Add Challenge":
   - Fill in challenge details (name, description, category)
   - Set point values (initial, minimum for dynamic scoring)
   - Configure challenge type (standard, dynamic, scripted)
   - Add flags (exact match, regex, case-insensitive options)
   - Upload attachments or provide download links
   - Add hints (optional)

5. **Manage challenge visibility** by setting state (hidden, visible, locked).

### Team Management

1. **Configure team settings** in the event configuration:
   - Team size limits
   - Team formation rules
   - Team visibility options

2. **Manage teams** from the admin dashboard:
   - View all teams
   - Edit team details
   - Disable/enable teams
   - Review team members

3. **Export team data** for analytics or reporting.

### User Management

1. **Access user management** from the admin dashboard.

2. **Manage users**:
   - View all registered users
   - Edit user details and roles
   - Disable/enable accounts
   - Reset passwords

3. **Export user data** for analytics or reporting.

## Development

### Code Structure

DCTFd follows a standard Django project structure:

- **Django Apps**:
  - `challenges/`: Challenge models, views, and logic
  - `core/`: Core platform functionality
  - `event/`: Event management
  - `teams/`: Team management
  - `users/`: User management
  - `organizer/`: Organizer dashboard
  - `superadmin/`: Administrative functions

- **Frontend Assets**:
  - `static/`: Static assets (CSS, JS, images)
  - `templates/`: HTML templates
  - `media/`: User-uploaded files

### Database Migrations

After making changes to models:

1. **Create migrations**:
   ```bash
   python manage.py makemigrations
   ```

2. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

### Avatar System

DCTFd includes an avatar system for users and teams:

1. **Load default avatars**:
   ```bash
   python load_avatars.py
   ```

2. **Avatar structure**:
   - Place avatars in `media/avatars/` directory
   - Create subdirectories for categories
   - Supported formats: PNG, JPG, JPEG, SVG

3. **Customizing avatars**:
   - Add your custom avatars to the appropriate directories
   - Run the load script to update the database

### Custom Features

To add custom features:

1. **Create a new Django app** if the feature is substantial:
   ```bash
   python manage.py startapp myfeature
   ```

2. **Add the app to `INSTALLED_APPS`** in settings.

3. **Create models, views, and templates** as needed.

4. **Include URLs** in the main URLconf.

5. **Create and apply migrations**.

### Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong, unique `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set secure cookie settings
- [ ] Configure proper database access controls
- [ ] Set up firewall rules
- [ ] Implement rate limiting
- [ ] Enable CSRF protection
- [ ] Set up regular security updates
- [ ] Configure proper file upload permissions
- [ ] Implement backup strategy

## Contributing

Want to help make DCTFd better? Awesome! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines on how to get involved.

We welcome all kinds of contributions - from code and documentation to design and testing. Even if you're new to open source or Django, there's probably something you can help with!

## License

DCTFd is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ by Srivatsan Sk | Copyright (c) 2025 | MIT License
