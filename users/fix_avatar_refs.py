"""
Fix the database state manually for avatar migration
"""

import sqlite3
import os
from django.conf import settings

def main():
    """
    Connect directly to the database and fix the avatar references
    """
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the avatar_id column exists
    cursor.execute("PRAGMA table_info(users_baseuser)")
    columns = cursor.fetchall()
    avatar_id_exists = any(column[1] == 'avatar_id' for column in columns)
    
    if avatar_id_exists:
        # If it exists, set it to NULL
        cursor.execute("UPDATE users_baseuser SET avatar_id = NULL")
        print(f"Reset avatar_id for {cursor.rowcount} users")
    else:
        print("No avatar_id column found, migrations should proceed normally")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Set up Django environment
    import sys
    import django

    # Add the project directory to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Configure Django settings
    os.environ.setdefault("DJANGO_ENVIRONMENT", "development")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCTFd.settings")
    django.setup()

    main()
