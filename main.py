import bcrypt  # Import bcrypt for password hashing
import gradio as gr
import sqlite3
import os
import re  # Import regex module for validation
import random  # For generating OTPs
import requests  # For sending messages via Telegram Bot API

# Global dictionary to store OTPs for users
otp_storage = {}
telegram_config = {"bot_token": "8118474160:AAHJhgx9N735q_cmAhGTrr_vpNmSHmsM6YY"}  # Store Telegram Bot token

# Hash a password before storing it in the database
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verify a password during login
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Initialize the database
def init_db():
    db_path = os.path.join(os.path.dirname(__file__), "login_user.db")  # Use the new database file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT,
            telegram_chat_id TEXT
        )
    """)

    # Check if the telegram_chat_id column exists, and add it if missing
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if "telegram_chat_id" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN telegram_chat_id TEXT")

    # Insert default users with hashed passwords
    users = [
        ("admin", hash_password("labAdmin1!"), "admin", "123456789"),  # Replace with actual Telegram chat IDs
        ("superuser", hash_password("SuperPass2@"), "superuser", "987654321"),
        ("operator", hash_password("OperPass3#"), "operator", "1122334455")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO users (username, password, role, telegram_chat_id) VALUES (?, ?, ?, ?)
    """, users)
    conn.commit()
    conn.close()

# Send OTP via Telegram
def send_otp(telegram_chat_id):
    otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
    otp_storage[telegram_chat_id] = otp  # Store the OTP for verification

    # Telegram Bot Configuration
    bot_token = telegram_config["bot_token"]
    message = f"Your OTP for login is: {otp}"

    # Send the message via Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"DEBUG: OTP sent to Telegram chat ID {telegram_chat_id}")
            return "OTP sent successfully to your Telegram."
        else:
            print(f"ERROR: Failed to send OTP via Telegram. Response: {response.text}")
            return "Failed to send OTP via Telegram."
    except Exception as e:
        print(f"ERROR: Failed to send OTP: {str(e)}")
        return f"Failed to send OTP: {str(e)}"

# Verify OTP
def verify_otp(telegram_chat_id, otp):
    if telegram_chat_id in otp_storage and otp_storage[telegram_chat_id] == otp:
        del otp_storage[telegram_chat_id]  # Remove OTP after successful verification
        return True
    return False

# Define a login function
def login(username, password):
    db_path = os.path.join(os.path.dirname(__file__), "login_user.db")  # Use the new database file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role, telegram_chat_id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and verify_password(password, result[0]):
        telegram_chat_id = result[2]
        return f"Password verified. Welcome {username}!", result[1], telegram_chat_id
    else:
        return "Invalid username or password.", None, None

# Initialize the database
init_db()

# Create the Gradio interface
with gr.Blocks() as demo:
    login_status = gr.State(value=False)
    user_role = gr.State(value=None)
    user_telegram_chat_id = gr.State(value=None)

    # Step 1: Login Tab
    with gr.Tab("Login") as login_tab:
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Textbox(label="Login Status")

        def login_wrapper(username, password):
            message, role, telegram_chat_id = login(username, password)
            if role:
                return message, True, role, telegram_chat_id
            return message, False, None, None

        login_button.click(
            login_wrapper,
            inputs=[username_input, password_input],
            outputs=[login_output, login_status, user_role, user_telegram_chat_id]
        )

    # Step 2: OTP Tab
    with gr.Tab("OTP Verification") as otp_tab:
        otp_input = gr.Textbox(label="Enter OTP")
        otp_button = gr.Button("Verify OTP")
        otp_output = gr.Textbox(label="OTP Verification Status")

        def otp_wrapper(telegram_chat_id, otp):
            if verify_otp(telegram_chat_id, otp):
                return "OTP verified successfully!", True
            return "Invalid OTP. Please try again.", False

        otp_button.click(
            otp_wrapper,
            inputs=[user_telegram_chat_id, otp_input],
            outputs=[otp_output, login_status]
        )

    # Step 3: User Management Tab
    with gr.Tab("User Management") as user_management_tab:
        gr.Markdown("#### Add, Delete, or Edit Users")
        new_username = gr.Textbox(label="New Username")
        new_password = gr.Textbox(label="New Password", type="password")
        new_role = gr.Textbox(label="Role")
        new_telegram_chat_id = gr.Textbox(label="Telegram Chat ID")
        add_user_button = gr.Button("Add User")
        add_user_output = gr.Textbox(label="Add User Status")

        def add_user(username, password, role, telegram_chat_id):
            db_path = os.path.join(os.path.dirname(__file__), "login_user.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, role, telegram_chat_id) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, role, telegram_chat_id),
                )
                conn.commit()
                return f"User {username} added successfully!"
            except sqlite3.IntegrityError:
                return f"Error: User {username} already exists."
            finally:
                conn.close()

        add_user_button.click(
            add_user,
            inputs=[new_username, new_password, new_role, new_telegram_chat_id],
            outputs=add_user_output,
        )

    # Step 4: Greeting Tab
    with gr.Tab("Greeting") as greeting_tab:
        name_input = gr.Textbox(label="Enter your name")
        greet_button = gr.Button("Greet")
        greet_output = gr.Textbox(label="Greeting")

        def greet(name):
            return f"Hello, {name}!"

        greet_button.click(
            greet,
            inputs=[name_input],
            outputs=[greet_output],
        )

    # Control Tab Visibility
    def update_visibility(login_status):
        return (
            gr.update(visible=True),               # Login tab visibility (always visible)
            gr.update(visible=login_status),       # OTP tab visibility
            gr.update(visible=login_status),       # User Management tab visibility
            gr.update(visible=login_status),       # Greeting tab visibility
        )

    login_status.change(
        update_visibility,
        inputs=[login_status],
        outputs=[login_tab, otp_tab, user_management_tab, greeting_tab]
    )

demo.launch(share=True)