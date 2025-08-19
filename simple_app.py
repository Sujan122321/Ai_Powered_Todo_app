import streamlit as st
import pandas as pd
from src.database import *
from src.gemini_client import categorize_task
# Initialize database
init_db()

# Streamlit UI
st.set_page_config(page_title="AI To-Do List", layout="centered")
st.title("📝 AI Powered To-Do List")

# Add Task Section
st.subheader("➕ Add New Task")
new_task = st.text_input("What do you need to do?")

if st.button("Add Task") and new_task.strip():
    # Use AI to categorize
    category, priority = categorize_task(new_task)
    
    # Add to database
    add_task(new_task, priority, category)
    st.success(f"✅ Task added! ({priority} priority, {category} category)")
    st.rerun()

# Display Tasks
st.subheader("📋 Your Tasks")
tasks_data = fetch_tasks()

if tasks_data:
    # Convert database rows to list of dictionaries
    tasks = []
    for task in tasks_data:
        tasks.append({
            "id": task[0],
            "description": task[1],
            "priority": task[2],
            "category": task[3],
            "done": task[4],
            "created_at": task[5]
        })
    
    # Create a nice display table
    df = pd.DataFrame(tasks)
    df_display = df.copy()
    df_display["Status"] = df_display["done"].apply(lambda x: "✅ Done" if x else "⏳ Pending")
    
    # Add emojis for categories
    category_emojis = {
        "Work": "💼",
        "Study": "📚", 
        "Personal": "🏠",
        "Health": "🏥"
    }
    df_display["Category"] = df_display["category"].apply(
        lambda x: f"{category_emojis.get(x, '📌')} {x}"
    )
    
    # Add color for priorities
    priority_colors = {
        "High": "🔴 High",
        "Medium": "🟡 Medium", 
        "Low": "🟢 Low"
    }
    df_display["Priority"] = df_display["priority"].apply(
        lambda x: priority_colors.get(x, x)
    )
    
    # Show the table (hide ID and raw done status)
    st.table(df_display[["description", "Priority", "Category", "Status"]])
    
    # Task Management
    st.subheader("⚙️ Manage Tasks")
    
    # Create a dropdown for task selection
    task_options = [f"{i+1}. {task['description'][:50]}{'...' if len(task['description']) > 50 else ''}" 
                   for i, task in enumerate(tasks)]
    selected_task = st.selectbox("Select a task:", task_options)
    
    if selected_task:
        task_index = task_options.index(selected_task)
        task_id = tasks[task_index]["id"]
        current_status = tasks[task_index]["done"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Toggle Done/Undone"):
                update_task_status(task_id, not current_status)
                st.rerun()
                
        with col2:
            if st.button("🗑️ Delete Task"):
                delete_task(task_id)
                st.rerun()

else:
    st.info("No tasks yet! Add a task above to get started.")

# Statistics
if tasks_data:
    st.subheader("📊 Statistics")
    total_tasks = len(tasks_data)
    completed_tasks = sum(1 for task in tasks_data if task[4])  # task[4] is done status
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tasks", total_tasks)
    with col2:
        st.metric("Completed", completed_tasks)
    
    if total_tasks > 0:
        progress = completed_tasks / total_tasks
        st.progress(progress)

# Footer
st.write("---")
st.write("✨ Powered by Gemini AI + PostgreSQL | Designed by @Sujan Shrestha")