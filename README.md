# User Management and Greeting Application

This project is a Python-based web application built using the [Gradio](https://gradio.app/) library. It provides a user-friendly interface for managing users and greeting them. The application includes role-based access control for user management features.

## Features

1. **Login System**:
    - Users can log in with a username and password.
    - Role-based access control is implemented.
    - Only the **Login** tab is visible until the user logs in successfully.

2. **User Management**:
    - Add new users (only accessible to `superuser` role).
    - Delete existing users (only accessible to `superuser` role).
    - Edit user details (only accessible to `superuser` role).

3. **Greeting**:
    - A simple greeting feature where users can input their name and receive a personalized greeting.

4. **Database**:
    - SQLite is used to store user credentials and roles.
    - Default users are created during initialization:
      - `admin` (password: `lab`, role: `admin`)
      - `superuser` (password: `superpass`, role: `superuser`)
      - `operator` (password: `operpass`, role: `operator`)

5. **Dynamic Tab Visibility**:
    - The **User Management** and **Greeting** tabs are hidden until the user logs in successfully.

## Installation

1. Clone the repository or download the code.
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python main.py
    ```

## Usage

### Login
1. Open the application in your browser (it will launch automatically).
2. Navigate to the **Login** tab.
3. Enter your username and password to log in.

### User Management
1. After logging in as a `superuser`, navigate to the **User Management** tab.
2. Use the following features:
    - **Add User**: Enter a new username, password, and role, then click "Add User".
    - **Delete User**: Enter the username of the user to delete, then click "Delete User".
    - **Edit User**: Enter the username, new password, and new role, then click "Edit User".

### Greeting
1. Navigate to the **Greeting** tab.
2. Enter your name and receive a personalized greeting.

## Role-Based Access Control

- **Superuser**: Can add, delete, and edit users.
- **Admin** and **Operator**: Can log in but cannot manage users.

## File Structure

- `main.py`: The main application file containing all the logic.
- `db_file/users.db`: SQLite database file (created automatically on first run).
- `requirements.txt`: File containing the required dependencies.

## Security Notes

- Passwords are stored in plain text in the database. For production use, consider hashing passwords using libraries like `bcrypt` or `hashlib`.
- Input validation is implemented for usernames (only letters are allowed).

## Dependencies

- [Gradio](https://gradio.app/): For building the web interface.
- SQLite: For database management.

## Default Users

| Username   | Password   | Role       |
|------------|------------|------------|
| admin      | lab        | admin      |
| superuser  | superpass  | superuser  |
| operator   | operpass   | operator   |

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Gradio](https://gradio.app/) for providing an easy-to-use interface library.
- SQLite for lightweight database management.
