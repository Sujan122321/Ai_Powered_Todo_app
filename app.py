import streamlit as st
import pandas as pd
from src.database import *
from src.gemini_client import categorize_task
import time
from datetime import datetime

# Initialize database
init_db()

# Streamlit UI Configuration
st.set_page_config(
    page_title="AI To-Do List Pro", 
    layout="wide",
    page_icon="✅",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #4B0082;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #6A0DAD;
        border-bottom: 2px solid #9370DB;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .task-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .success-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation and settings
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/todo-list.png", width=100)
    st.title("🎯 AI To-Do Pro")
    st.write("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    if st.button("🔄 Refresh Page"):
        st.rerun()
    
    st.write("---")
    st.subheader("📊 View Options")
    show_completed = st.checkbox("Show Completed Tasks", value=True)
    sort_by = st.selectbox("Sort By", ["Newest First", "Priority", "Category"])
    
    st.write("---")
    st.subheader("🎨 Theme")
    theme = st.radio("Choose Theme", ["Default", "Dark Mode", "Light Mode"])
    
    st.write("---")
    st.info("💡 Tip: Use descriptive task names for better AI categorization!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h1 class="main-header">🚀 AI Powered To-Do List</h1>', unsafe_allow_html=True)
    
    # Add Task Section with card design
    with st.container():
        st.markdown('<h2 class="sub-header">✨ Add New Task</h2>', unsafe_allow_html=True)
        
        task_col1, task_col2 = st.columns([3, 1])
        with task_col1:
            new_task = st.text_input(
                "📝 Enter your task:", 
                placeholder="e.g., Complete project report by Friday",
                help="Be specific for better AI categorization!"
            )
        
        with task_col2:
            st.write("")
            st.write("")
            if st.button("🚀 Add Task", use_container_width=True):
                if new_task.strip():
                    with st.spinner("🤖 AI is categorizing your task..."):
                        category, priority = categorize_task(new_task)
                        time.sleep(0.5)  # Simulate processing
                        
                        # Add to database
                        add_task(new_task, priority, category)
                        
                        # Success animation
                        success_placeholder = st.empty()
                        success_placeholder.markdown(
                            f'<div class="success-message">✅ Task added! '
                            f'<br>Priority: {priority} | Category: {category}</div>', 
                            unsafe_allow_html=True
                        )
                        time.sleep(2)
                        success_placeholder.empty()
                        st.rerun()
                else:
                    st.warning("⚠️ Please enter a task description!")

# Display Tasks
st.markdown('<h2 class="sub-header">📋 Your Tasks</h2>', unsafe_allow_html=True)

tasks_data = fetch_tasks()

if tasks_data:
    # Convert to list of dictionaries
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
    
    # Filter completed tasks if needed
    if not show_completed:
        tasks = [task for task in tasks if not task["done"]]
    
    # Sort tasks
    if sort_by == "Priority":
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))
    elif sort_by == "Category":
        tasks.sort(key=lambda x: x["category"])
    else:  # Newest first
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Display tasks in cards
    for i, task in enumerate(tasks):
        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(task["priority"], "⚪")
        category_emoji = {"Work": "💼", "Study": "📚", "Personal": "🏠", "Health": "🏥"}.get(task["category"], "📌")
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status_emoji = "✅" if task["done"] else "⏳"
                st.markdown(f"""
                <div class="task-card">
                    <h3>{status_emoji} {task['description']}</h3>
                    <p>{priority_emoji} {task['priority']} Priority | {category_emoji} {task['category']}</p>
                    <small>Added: {task['created_at'].strftime('%Y-%m-%d %H:%M') if hasattr(task['created_at'], 'strftime') else task['created_at']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"🔄 Toggle", key=f"toggle_{task['id']}"):
                    update_task_status(task['id'], not task["done"])
                    st.rerun()
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{task['id']}"):
                    delete_task(task['id'])
                    st.rerun()

else:
    st.info("🎉 No tasks yet! Add your first task above to get started.")

# Statistics and Analytics
if tasks_data:
    st.markdown('<h2 class="sub-header">📊 Productivity Dashboard</h2>', unsafe_allow_html=True)
    
    total_tasks = len(tasks_data)
    completed_tasks = sum(1 for task in tasks_data if task[4])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="stat-card"><h3>📋 Total</h3><h2>{total_tasks}</h2></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="stat-card"><h3>✅ Completed</h3><h2>{completed_tasks}</h2></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="stat-card"><h3>📈 Progress</h3><h2>{completion_rate:.1f}%</h2></div>', unsafe_allow_html=True)
    
    with col4:
        pending = total_tasks - completed_tasks
        st.markdown(f'<div class="stat-card"><h3>⏳ Pending</h3><h2>{pending}</h2></div>', unsafe_allow_html=True)
    
    # Progress bar
    st.progress(completion_rate / 100)
    
    # Category distribution
    if tasks:
        category_counts = pd.DataFrame(tasks)['category'].value_counts()
        st.bar_chart(category_counts)

# Footer with enhanced design
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h3>✨ Powered by Gemini AI + PostgreSQL</h3>
        <p>🚀 Designed with ❤️ by @Sujan Shrestha</p>
        <p>⭐ Star this project on GitHub | 📧 Contact: sujan@example.com</p>
    </div>
    """, unsafe_allow_html=True)

# Add some interactive elements
with st.expander("🎮 Quick Tips & Shortcuts"):
    st.write("""
    - **Double-click** a task to edit (coming soon!)
    - Use **descriptive language** for better AI categorization
    - **Color codes**: 🔴 High, 🟡 Medium, 🟢 Low priority
    - **Categories**: 💼 Work, 📚 Study, 🏠 Personal, 🏥 Health
    """)

# Add a fun confetti effect on task completion (simulated)
if st.button("🎉 Celebrate Progress!"):
    st.balloons()
    st.success("🎊 Keep up the great work! 🎊")