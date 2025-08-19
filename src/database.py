# Connecting  to the postgres database

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Database connection established successfully.")
        return conn
    
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Creating a task table 
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL,
            priority VARCHAR(10) NOT NULL,
            category VARCHAR(10) NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close() 

# Implement CRUD Operations
# 1: Add a task

def add_task(description, priority, category):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (description, priority, category) VALUES (%s, %s, %s)",
        (description, priority, category)
    )
    conn.commit()
    conn.close()
    
# 2: Fetch all the tasks
def fetch_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# 3: Update a task status (Toggle Done)
def update_task_status(task_id, done):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET done = %s WHERE id = %s",
        (done, task_id)
    )
    conn.commit()
    conn.close()
    
# 4: Delete a task
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()