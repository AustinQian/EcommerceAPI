# Authentication API Documentation

This document describes the endpoints provided by the authentication API. The API handles user registration, login, email verification, and password reset functionality.

---

## Base URL

- **Production:** `https://yourdomain.com/api/auth`
- **Development:** `http://localhost:5000/api/auth`

All endpoints are prefixed with `/api/auth`.

---

## Endpoints

### 1. Register User

- **URL:** `/register`
- **Method:** `POST`
- **Description:** Registers a new user by creating an account and sending a verification email.
- **Request Headers:**
  - `Content-Type: application/json`
- **Request Body Example:**

  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }
  ```

- **Success Response:**
  - **Status Code:** `201 Created`
  - **Response Body:**

    ```json
    {
      "message": "User registered successfully. Please verify your email."
    }
    ```

- **Error Responses:**
  - **401 Unauthorized:**  
    - Username already exists  
    - Email already registered
  - **400 Bad Request:**  
    - Missing required fields  
    - Passwords do not match  
    - Invalid email format  
    - Password does not meet complexity requirements
  - **500 Internal Server Error:**  
    - Email sending failure

---

### 2. Login User

- **URL:** `/login`
- **Method:** `POST`
- **Description:** Authenticates an existing user and returns a JWT access token.
- **Request Headers:**
  - `Content-Type: application/json`
- **Request Body Example:**

  ```json
  {
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }
  ```

- **Success Response:**
  - **Status Code:** `200 OK`
  - **Response Body:**

    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

- **Error Responses:**
  - **401 Unauthorized:**  
    - Email not found  
    - Invalid email format  
    - Incorrect password
  - **403 Forbidden:**  
    - Email not verified

---

### 3. Verify Email

- **URL:** `/verify/<token>`
- **Method:** `GET`
- **Description:** Verifies the user's email address using a token sent by email.
- **URL Parameter:**
  - `<token>`: The email verification token.
- **Success Response:**
  - **Status Code:** `200 OK`
  - **Response Body:**

    ```json
    {
      "message": "Email successfully verified."
    }
    ```

- **Error Responses:**
  - **400 Bad Request:**  
    - Invalid or expired verification link.
  - **404 Not Found:**  
    - User not found.
  - **200 OK (if already verified):**  
    - Message indicating that the email is already verified.

---

### 4. Request Password Reset

- **URL:** `/reset_request`
- **Method:** `POST`
- **Description:** Sends a password reset link to the user's email.
- **Request Headers:**
  - `Content-Type: application/json`
- **Request Body Example:**

  ```json
  {
    "email": "john@example.com"
  }
  ```

- **Success Response:**
  - **Status Code:** `200 OK`
  - **Response Body:**

    ```json
    {
      "message": "Password reset link sent to your email"
    }
    ```

- **Error Response:**
  - **404 Not Found:**  
    - Email not found

---

### 5. Reset Password

- **URL:** `/reset_password/<token>`
- **Methods:** `GET`, `POST`
- **Description:**  
  - **GET:** Validates the reset token and informs the client that the token is valid (client should then redirect to a password reset form).  
  - **POST:** Resets the password using the provided token.
- **URL Parameter:**
  - `<token>`: The password reset token.
- **GET Request Success Response:**
  - **Status Code:** `200 OK`
  - **Response Body:**

    ```json
    {
      "message": "Token is valid. Redirect to password reset form."
    }
    ```

- **POST Request Body Example:**

  ```json
  {
    "password": "NewSecurePassword123!",
    "confirm_password": "NewSecurePassword123!"
  }
  ```

- **POST Request Success Response:**
  - **Status Code:** `200 OK`
  - **Response Body:**

    ```json
    {
      "message": "Password reset successful"
    }
    ```

- **Error Responses:**
  - **400 Bad Request:**  
    - Invalid or expired token.
  - **404 Not Found:**  
    - User not found.
  - **401 Unauthorized:**  
    - New password does not match confirm password.

---

## Additional Notes

- **Password Security:**  
  Passwords must be at least 8 characters long and include a mix of letters, numbers, and symbols.
  
- **Token Handling:**  
  - **Email Verification:** Tokens are generated and sent via email for account verification.
  - **JWT for Login:** Upon successful login, a JWT access token is returned.
  - **Password Reset:** Separate tokens are used for password reset requests and are verified before updating the password.

- **Validation:**  
  Email and password formats are validated using helper functions in the `services.validation` module.

- **Error Handling:**  
  API responses return clear error messages and proper HTTP status codes based on the type of failure.

---

This documentation serves as a template for your authentication API. You can customize and expand it to include further details such as request/response examples for edge cases, rate limiting information, and security considerations.