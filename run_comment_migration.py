"""
Helper script to run comment system migration

This script will:
1. Check current migration status
2. Run the new migration
3. Verify tables and columns created
"""

import os
import sys

def run_migration():
    print("=" * 60)
    print("COMMENT SYSTEM MIGRATION HELPER")
    print("=" * 60)
    
    print("\n📋 Step 1: Checking migration status...")
    os.system("flask db current")
    
    print("\n📋 Step 2: Running upgrade...")
    result = os.system("flask db upgrade")
    
    if result != 0:
        print("\n❌ Migration failed!")
        print("\nTroubleshooting:")
        print("1. Check if database is running")
        print("2. Check migrations/versions/ folder")
        print("3. Try: flask db downgrade (then upgrade again)")
        print("4. Check Flask logs for errors")
        return False
    
    print("\n✅ Migration completed successfully!")
    
    print("\n📋 Step 3: Verifying database schema...")
    os.system("python test_comment_system.py")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start your Flask server: python app.py")
    print("2. Visit a comic page")
    print("3. Try posting a comment")
    print("4. Try replying to a comment")
    print("5. Try liking/disliking")
    print("\n📖 See COMMENT_SYSTEM_README.md for full documentation")
    
    return True

if __name__ == "__main__":
    try:
        run_migration()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
