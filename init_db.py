import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def init_database():
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Do@n33203'
    )
    
    try:
        with connection.cursor() as cursor:
            # Drop and recreate database
            cursor.execute("DROP DATABASE IF EXISTS comic_web")
            cursor.execute("CREATE DATABASE comic_web")
            cursor.execute("USE comic_web")
            
            # Create tables
            cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    email VARCHAR(120) NOT NULL,
                    password_hash VARCHAR(256) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY idx_username (username),
                    UNIQUE KEY idx_email (email)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE comics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(100),
                    description TEXT,
                    cover_image VARCHAR(500),
                    genre VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    views INT DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'ongoing',
                    rating FLOAT DEFAULT 0.0,
                    tags VARCHAR(500)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE chapters (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    comic_id INT NOT NULL,
                    chapter_number FLOAT NOT NULL,
                    title VARCHAR(200),
                    image_urls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    views INT DEFAULT 0,
                    FOREIGN KEY (comic_id) REFERENCES comics(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE user_read_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    comic_id INT NOT NULL,
                    chapter_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (comic_id) REFERENCES comics(id) ON DELETE CASCADE,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
                )
            """)
            
            connection.commit()
            print("Database initialized successfully!")
            return True
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
        
    finally:
        connection.close()

if __name__ == "__main__":
    success = init_database()
    if not success:
        print("Failed to initialize database.")