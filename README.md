# DCTFd - CTF Platform

DCTFd is a Capture The Flag platform modeled after CTFd, built with Django.

Developed by Srivatsan Sk | Copyright (c) 2025 | MIT License

## Setting Up Your First Event

1. Run migrations:
   ```
   python manage.py migrate
   ```

2. Start the development server:
   ```
   python manage.py runserver
   ```

3. Navigate to the event setup page:
   ```
   http://localhost:8000/event/setup/
   ```

4. Fill out the setup form to configure your first CTF event:
   - Event details (name, description, format)
   - Time settings (start/end times, registration period)
   - Root admin account
   - Appearance settings (theme, colors, logo, banner)
   - Advanced settings

5. After submitting the form, review your settings on the confirmation page.

6. Click "Confirm and Create" to complete the setup.

7. You'll be redirected to the admin panel where you can log in with your newly created admin account.

## Next Steps

After setting up your event, you can:

1. Add challenges
2. Create challenge categories
3. Configure more detailed settings
4. Add event pages
5. Monitor registrations

## Development

To make changes to the code:

1. Create migrations after model changes:
   ```
   python manage.py makemigrations
   ```

2. Apply migrations:
   ```
   python manage.py migrate
   ```

3. Create a superuser (if not done through setup):
   ```
   python manage.py createsuperuser
   ```

## Architecture

DCTFd follows a standard Django project structure:

- **apps/**: Django applications for different components
  - **challenges/**: Challenge models, views, and logic
  - **core/**: Core platform functionality
  - **event/**: Event management
  - **teams/**: Team management
  - **users/**: User management
- **media/**: User-uploaded files
- **static/**: Static assets
- **templates/**: HTML templates

## Production Deployment

For production deployment, follow these steps:

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```
   cp .env.template .env
   # Edit .env with your production settings
   ```

3. Run the production preparation command:
   ```
   python manage.py prepare_production --all
   ```

4. Set the environment variable for production settings:
   ```
   export DJANGO_SETTINGS_MODULE=DCTFd.settings_production
   ```

5. Run migrations and collect static files:
   ```
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```

6. Configure a web server (Nginx, Apache) with Gunicorn or uWSGI.

For detailed instructions, see [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) and [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md).
