import gradio as gr
import sqlite3
import os
import re  # Import regex module for validation

# Initialize the database
def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "db_file", "users.db")
    if not os.path.exists(db_path):  # Use existing file if it exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure the directory exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT
            )
        """)
        # Insert default users with roles if not exists
        users = [
            ("<username1>", "<password1>", "admin"),
            ("<username2>", "<password2>", "superuser"),
            ("<username3>", "<password3>", "operator")
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)
        """, users)
        conn.commit()
        conn.close()

# Define a login function
def login(username, password):
    db_path = os.path.join(os.path.dirname(__file__), "db_file", "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == password:
        role = result[1]
        return f"Welcome {username}! You are logged in as {role}.", role
    else:
        return "Invalid username or password.", None

# Define a function to add new users
def add_user(username, password, role):
    if not re.match("^[A-Za-z]+$", username):
        return "Error: Username must contain only letters (no spaces or special characters)."

    db_path = os.path.join(os.path.dirname(__file__), "db_file", "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role) VALUES (?, ?, ?)
        """, (username, password, role))
        conn.commit()
        return f"User {username} added successfully!"
    except sqlite3.IntegrityError:
        return f"Error: User {username} already exists."
    finally:
        conn.close()

# Define a function to delete users
def delete_user(username):
    db_path = os.path.join(os.path.dirname(__file__), "db_file", "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return f"User {username} deleted successfully!" if cursor.rowcount > 0 else f"Error: User {username} not found."

# Define a function to edit users
def edit_user(username, new_password, new_role):
    db_path = os.path.join(os.path.dirname(__file__), "db_file", "users.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET password = ?, role = ? WHERE username = ?
    """, (new_password, new_role, username))
    conn.commit()
    conn.close()
    return f"User {username} updated successfully!" if cursor.rowcount > 0 else f"Error: User {username} not found."

# Define a simple function for the UI
def greet(name):
    return f"Hello, {name}!"

# Initialize the database
init_db()

# Wrapper functions for role-based access control
def add_user_wrapper(username, password, role, user_role):
    if user_role != "superuser":
        return "Access Denied: You do not have permission to add users."
    return add_user(username, password, role)

def delete_user_wrapper(username, user_role):
    if user_role != "superuser":
        return "Access Denied: You do not have permission to delete users."
    return delete_user(username)

def edit_user_wrapper(username, new_password, new_role, user_role):
    if user_role != "superuser":
        return "Access Denied: You do not have permission to edit users."
    return edit_user(username, new_password, new_role)

# Create the Gradio interface
with gr.Blocks() as demo:
    login_status = gr.State(value=False)
    user_role = gr.State(value=None)

    with gr.Tab("Login") as login_tab:
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Textbox(label="Login Status")

        def login_wrapper(username, password):
            message, role = login(username, password)
            if role:
                return message, True, role
            return message, False, None

        login_button.click(
            login_wrapper,
            inputs=[username_input, password_input],
            outputs=[login_output, login_status, user_role]
        )

    with gr.Tab("User Management") as user_management_tab:
        gr.Markdown("#### Add, Delete, or Edit Users")
        with gr.Row():
            new_username = gr.Textbox(label="New Username")
            new_password = gr.Textbox(label="New Password", type="password")
            new_role = gr.Textbox(label="Role")
            add_user_status = gr.Textbox(label="Add User Status")
            add_user_button = gr.Button("Add User")

            username_to_delete = gr.Textbox(label="Username to Delete")
            delete_user_status = gr.Textbox(label="Delete User Status")
            delete_user_button = gr.Button("Delete User")

            username_to_edit = gr.Textbox(label="Username to Edit")
            edit_new_password = gr.Textbox(label="New Password", type="password")
            edit_new_role = gr.Textbox(label="New Role")
            edit_user_status = gr.Textbox(label="Edit User Status")
            edit_user_button = gr.Button("Edit User")

            add_user_button.click(
                add_user_wrapper,
                inputs=[new_username, new_password, new_role, user_role],
                outputs=add_user_status
            )
            delete_user_button.click(
                delete_user_wrapper,
                inputs=[username_to_delete, user_role],
                outputs=delete_user_status
            )
            edit_user_button.click(
                edit_user_wrapper,
                inputs=[username_to_edit, edit_new_password, edit_new_role, user_role],
                outputs=edit_user_status
            )

    with gr.Tab("Greeting") as greeting_tab:
        greet_interface = gr.Interface(
            fn=greet,
            inputs=gr.Textbox(label="Enter your name"),
            outputs=gr.Textbox(label="Greeting")
        )
        greet_interface.render()

    # Hide all tabs except login until login is successful
    def update_visibility(login_status):
        return (
            gr.update(visible=True),               # Login tab visibility (always visible)
            gr.update(visible=login_status),       # User Management tab visibility
            gr.update(visible=login_status)        # Greeting tab visibility
        )

    login_status.change(
        update_visibility,
        inputs=[login_status],
        outputs=[login_tab, user_management_tab, greeting_tab]
    )

demo.launch()