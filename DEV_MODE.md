# DCTFd Development Mode

This document explains how to use the development mode feature of DCTFd.

## What is Development Mode?

Development mode is a special configuration that automatically sets up a pre-configured CTF environment with:

- Default admin user
- Sample event with reasonable settings
- Sample challenges and categories
- Test team
- Visual indicator that you're in development mode

This allows you to focus on developing specific features without having to manually set up the basic environment each time.

## How to Use Development Mode

### Enabling Development Mode

```bash
# Turn development mode ON
python manage.py devmode on

# Start the server
python manage.py runserver
```

When you first access the application in development mode, it will:

1. Automatically create a default admin user (username: admin, password: admin)
2. Set up a sample event with standard settings
3. Create sample categories and challenges
4. Redirect you to the admin login page

### Disabling Development Mode

```bash
# Turn development mode OFF
python manage.py devmode off

# Start the server
python manage.py runserver
```

## Development Mode Features

### Default Admin Credentials

- Username: `admin`
- Password: `admin`

### Default Event Settings

- Event Name: Development CTF
- Status: Active
- Registration: Open
- Team Formation: Allowed (1-4 members)
- Individual Participation: Allowed

### Sample Data

- 5 challenge categories (Web, Crypto, Reverse Engineering, Binary Exploitation, Forensics)
- 3 sample challenges with flags
- 1 test team

### Visual Indicators

- "Development Mode" indicator in the corner of every page
- Custom styling to distinguish development from production

## Security Warning

Development mode uses simplified settings and credentials that are **NOT SECURE** for production use. Always disable development mode before deploying to production or exposing your instance to the internet.

## Customizing Development Mode

To customize what gets created in development mode, you can modify the `setup_dev.py` management command located at:

```
core/management/commands/setup_dev.py
```

Here you can adjust:
- Default user credentials
- Event settings
- Sample challenges
- Categories
- Any other initialization data
