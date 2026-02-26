"""Database setup script for PostgreSQL"""
import os
from dotenv import load_dotenv
from packages.database import get_database

# Load environment variables
load_dotenv()

def setup():
    """Setup database tables"""
    print("Setting up PostgreSQL database...")
    
    try:
        db = get_database()
        print("✅ Database connected successfully")
        print("✅ Tables created successfully")
        print("\nDatabase is ready to use!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is installed and running")
        print("2. DATABASE_URL is set in .env file")
        print("3. Database exists (create with: createdb game_recommendation)")

if __name__ == "__main__":
    setup()
