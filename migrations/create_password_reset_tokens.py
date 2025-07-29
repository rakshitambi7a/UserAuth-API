"""
Migration to add password_reset_tokens table
Run this script to add password reset functionality to the database
"""
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_password_reset_tokens():
    """Add password_reset_tokens table to support password reset functionality"""
    
    # Get database path from environment or use default
    db_path = (os.getenv('DATABASE_PATH') or 
               os.getenv('DB_PATH') or 
               'users.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create password_reset_tokens table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        # Create index for faster token lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_password_reset_token 
        ON password_reset_tokens (token)
        ''')
        
        # Create index for user_id lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_password_reset_user_id 
        ON password_reset_tokens (user_id)
        ''')
        
        conn.commit()
        print("✓ Successfully created password_reset_tokens table")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating password_reset_tokens table: {e}")
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_password_reset_tokens()
