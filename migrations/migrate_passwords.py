import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import project modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from werkzeug.security import generate_password_hash
from db.database import Database

def migrate_plaintext_to_bcrypt():
    """
    Migrate all plaintext passwords to hashed passwords using werkzeug.
    This function identifies plaintext passwords and converts them to hashed passwords.
    """
    db = Database()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all users
            cursor.execute("SELECT id, email, password FROM users")
            users = cursor.fetchall()
            
            migration_count = 0
            
            for user_id, email, stored_password in users:
                # Check if password is already hashed
                if isinstance(stored_password, bytes):
                    stored_password = stored_password.decode('utf-8')
                    
                if stored_password.startswith("pbkdf2:sha256:"):
                    continue  # Skip already hashed passwords
                
                try:
                    # Generate hashed password
                    hashed_password = generate_password_hash(stored_password)
                except Exception as e:
                    print(f"Error hashing password for user {email} (ID: {user_id}): {e}")
                    continue
                
                # This is a plaintext password, convert to hashed password
                print(f"Migrating password for user {email} (ID: {user_id})")
                
                # Update the database
                try:
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
                    migration_count += 1
                except Exception as e:
                    print(f"Error updating password for user {email} (ID: {user_id}): {e}")
                    continue
            
            # Commit all changes
            conn.commit()
            
            print(f"\nMigration completed!")
            print(f"Total passwords migrated: {migration_count}")
            print(f"Total users processed: {len(users)}")
            
    except Exception as e:
        print(f"Error accessing the database: {e}")
        return

if __name__ == '__main__':
    # Run the migration
    migrate_plaintext_to_bcrypt()