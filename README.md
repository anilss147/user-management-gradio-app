# User Management and OTP Verification System

This project is a Python-based web application built using the [Gradio](https://gradio.app/) library. It provides a user-friendly interface for managing users, verifying OTPs via Telegram, and greeting users. The application includes role-based access control for user management features.

---

## **Features**

### **1. Login System**
- Users can log in with a username and password.
- Passwords are securely hashed using `bcrypt` before being stored in the database.
- Only the **Login** tab is visible until the user logs in successfully.

### **2. OTP Verification**
- After logging in, users must verify their identity using a One-Time Password (OTP).
- OTPs are sent to the user's Telegram account using a Telegram Bot.
- The Telegram Bot is configured using the provided bot token.

### **3. User Management**
- Admins can manage users through the **User Management Tab**:
  - Add new users with a username, password, role, and Telegram chat ID.
  - Future functionality for editing and deleting users can be added.
- Role-based access control can be implemented to restrict certain actions to specific roles (e.g., `admin`, `superuser`).

### **4. Greeting Tab**
- Users can enter their name in the **Greeting Tab** to receive a personalized greeting.

### **5. Database**
- SQLite is used to store user credentials, roles, and Telegram chat IDs.
- Default users are created during initialization:
  - `admin` (password: `labAdmin1!`, role: `admin`)
  - `superuser` (password: `SuperPass2@`, role: `superuser`)
  - `operator` (password: `OperPass3#`, role: `operator`)

---

## **Installation**

### **1. Prerequisites**
- Python 3.10 or higher
- Required Python packages:
  - `bcrypt`
  - `gradio`
  - `sqlite3` (built-in with Python)
  - `requests`

### **2. Installation Steps**
1. Clone the repository or download the source code:
   ```bash
   git clone https://github.com/anilss147/user-management-gradio-app.git
   cd your-repository-name