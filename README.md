TO use this API, run `pip install reuqirements.txt` and configure your database

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
    "password": "SecurePassword123!",
    "remember": "true"
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

# Group Buying Discounts API

This API enables users to create, join, and apply discounts through a “group buying” mechanism. When enough participants join a group buy, the discount is activated and applied to the product’s price in the user’s cart.

---

## Table of Contents

1. [Create a Group Buy](#create-a-group-buy)
2. [Retrieve a Group Buy](#retrieve-a-group-buy)
3. [Join a Group Buy](#join-a-group-buy)
4. [Apply Group Buy Discount](#apply-group-buy-discount)
5. [Models](#models)
6. [Authentication](#authentication)
7. [Error Handling](#error-handling)

---

## Group Buying Discounts

### Overview
The Group Buying Discounts feature allows users to get a lower price when enough participants join a shared purchase. A unique link is generated for each group buy, enabling users to invite friends. Once the minimum participant threshold is reached, the discount is activated and applied to the product’s price in the user’s cart.

### Key Features
- **Unique Invitation Link**: Each group buy generates a short, shareable link.
- **Minimum Participants**: A required number of users must join to activate the discount.
- **Automatic Discount Application**: When the threshold is met, discounts are applied at checkout.
- **User Tracking**: Keeps record of who has joined each group buy.

### Endpoints

1. **Create a Group Buy**
   - **URL**: `POST /api/groupbuy`
   - **Description**: Creates a new group buy for a product.  
   - **Request Body** (JSON):
     ```json
     {
       "product_id": 1,
       "discount_percentage": 10,
       "min_participants": 5
     }
     ```
   - **Response** (201 Created):
     ```json
     {
       "message": "Group buy created",
       "group_buy_id": 1,
       "unique_link": "b1234f8e"
     }
     ```

2. **Retrieve a Group Buy**
   - **URL**: `GET /api/groupbuy/<unique_link>`
   - **Description**: Fetches details of a group buy by its unique link.
   - **Response** (200 OK):
     ```json
     {
       "id": 1,
       "product_id": 123,
       "discount_percentage": 10,
       "min_participants": 5,
       "current_participants": 2,
       "unique_link": "b1234f8e",
       "is_active": true
     }
     ```

3. **Join a Group Buy**
   - **URL**: `POST /api/groupbuy/join/<unique_link>`
   - **Description**: Lets an authenticated user join a group buy. Increments participant count.
   - **Response** (200 OK):
     ```json
     {
       "message": "Joined group buy successfully"
     }
     ```

4. **Apply Group Buy Discount**
   - **URL**: `POST /api/groupbuy/apply-discount/<cart_id>`
   - **Description**: Applies the discount to the specified cart item if the minimum participant threshold is met.
   - **Request Body** (JSON):
     ```json
     {
       "group_buy_id": 1
     }
     ```
   - **Response** (200 OK):
     ```json
     {
       "message": "Discount applied to cart item",
       "original_price": 100.0,
       "discounted_price": 90.0
     }
     ```


### Example Flow
1. **Seller/Admin** creates a group buy for a product (e.g., 10% off if 5 users join).  
2. **Unique Link** is generated (e.g., `b1234f8e`).  
3. **Users** share this link and join via `POST /api/groupbuy/join/<unique_link>`.  
4. Once the minimum participant threshold is reached, the discount is activated.  
5. **Users** can then apply the discount to their cart at checkout using `POST /api/groupbuy/apply-discount/<cart_id>`.

### Authentication & Security
- Endpoints that require the user to be logged in use session-based or JWT-based authentication.  
- If a user is not authenticated, the server returns a `401 Unauthorized` error for protected routes.

### Error Handling
- **400 Bad Request**: Missing fields, insufficient participants, or invalid data.  
- **401 Unauthorized**: User not authenticated when trying to join or apply discounts.  
- **404 Not Found**: Invalid group buy link or non-existent resource.  

---

**Note**: Integrate these routes into your existing Flask project, register the blueprint with a prefix (e.g., `/api/groupbuy`), and run database migrations to create the new tables. Adjust the logic to match your specific models (e.g., cart structure, user model) and desired user flow.

