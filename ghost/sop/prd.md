# Task Management System Product Requirement Doc

# Database Structure

The database will consist of two primary tables: Users and Tasks.
Users Table

    UserID: INT, PRIMARY KEY, AUTO_INCREMENT
    Username: VARCHAR(255), UNIQUE, NOT_NULL
    PasswordHash: VARCHAR(255), NOT_NULL
    Email: VARCHAR(255), UNIQUE, NOT_NULL
    CreationDate: DATETIME, NOT_NULL

Tasks Table

    TaskID: INT, PRIMARY KEY, AUTO_INCREMENT
    UserID: INT, FOREIGN KEY REFERENCES Users(UserID)
    Title: VARCHAR(255), NOT_NULL
    Description: TEXT, NULLABLE
    DueDate: DATE, NULLABLE
    Status: ENUM('Pending', 'Completed'), DEFAULT 'Pending'
    CreationDate: DATETIME, NOT_NULL

# API Route Structure

The system will provide RESTful endpoints for managing users and tasks.
User Routes

    POST /api/users/register - Registers a new user.
    POST /api/users/login - Authenticates a user and returns a token.
    GET /api/users/{userID} - Retrieves user details.

Task Routes

    POST /api/tasks - Creates a new task.
    GET /api/tasks/{taskID} - Retrieves a specific task.
    GET /api/tasks - Retrieves all tasks for the logged-in user.
    PUT /api/tasks/{taskID} - Updates a specific task.
    DELETE /api/tasks/{taskID} - Deletes a specific task.

# Business Logic
User Registration

    Validate the provided username and email for uniqueness and format.
    Hash the provided password.
    Create a new user in the Users table.
    Return the user ID and creation date.

User Login

    Validate the provided username and password.
    Generate an authentication token.
    Return the token to the user.

Task Creation

    Authenticate the user token.
    Validate the input data for the task (title is required).
    Create a new task in the Tasks table linked to the user.
    Return the task ID and creation date.

Task Retrieval

    Authenticate the user token.
    For a single task, verify the task belongs to the user. For all tasks, fetch only the tasks belonging to the user.
    Return the task(s) data.

Task Update

    Authenticate the user token.
    Validate the input data for the update.
    Verify the task belongs to the user.
    Update the task in the database.
    Return the updated task information.

Task Deletion

    Authenticate the user token.
    Verify the task belongs to the user.
    Delete the task from the database.
    Return a success message.