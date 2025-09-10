# Environment Configuration for DCTFd

This document explains how to configure DCTFd using environment variables.

## Using Environment Variables

DCTFd now supports configuration through environment variables, which can be set in a `.env` file at the root of the project.

### Setting up Development Mode

You can use the `devmode` management command to easily toggle between development and production modes:

```bash
# Turn development mode ON (creates/updates .env file)
python manage.py devmode on

# Turn development mode OFF (updates .env file)
python manage.py devmode off
```

### Manual Environment Configuration

You can also manually create or edit the `.env` file with the following variables:

```
# Basic Configuration
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,example.com

# Development Mode
DEV_MODE=True

# Database Configuration (optional)
DATABASE_URL=postgres://user:password@localhost:5432/dctfd

# Email Configuration (optional)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
```

### Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable/disable debug mode | `True` in dev, `False` in prod |
| `SECRET_KEY` | Django secret key | Auto-generated in dev |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Empty in dev |
| `DEV_MODE` | Enable/disable development mode | `True` in dev, `False` in prod |
| `DATABASE_URL` | Database connection string | SQLite in dev |
| `EMAIL_*` | Email configuration | None in dev |

## Production Deployment

For production deployment, you should:

1. Create a `.env` file with appropriate production settings
2. Set `DEV_MODE=False` and `DEBUG=False`
3. Set a strong `SECRET_KEY`
4. Configure `ALLOWED_HOSTS` with your domain
5. Configure a production database with `DATABASE_URL`

Example production `.env` file:

```
DEBUG=False
DEV_MODE=False
SECRET_KEY=your-secure-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/dctfd_prod
```

## Switching Between Configurations

You can maintain multiple environment files for different scenarios:

```bash
# Development
cp .env.dev .env

# Production
cp .env.prod .env
```

Or use the `devmode` command to quickly toggle between modes.
