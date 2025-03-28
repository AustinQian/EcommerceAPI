TO use this API, run `pip install reuqirements.txt` and configure your database

# API Documentation

This document describes the endpoints provided by the authentication API. The API handles user registration, login, email verification, and password reset functionality.

---

## Base URL

- **Production:** `https://yourdomain.com/api`
- **Development:** `http://localhost:5000/api`


---

## Authentication Endpoints
All endpoints in Authentication Endpoints are prefixed with `/auth`.

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

This API enables users to create, join, and apply discounts through a "group buying" mechanism. When enough participants join a group buy, the discount is activated and applied to the product's price in the user's cart.

## Endpoints

### GET /groupbuy/products
Get list of products available for group buy.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Product Name",
        "description": "Product Description",
        "price": 99.99,
        "stock": 50,
        "image_url": "http://example.com/image.jpg",
        "category": "Electronics"
    }
]
```

### POST /groupbuy/create
Create a new group buy for an existing product.

**Request Body:**
```json
{
    "product_id": 1,
    "min_participants": 5,
    "discount_percentage": 15.0,
    "end_date": "2024-12-31T23:59:59"  // Optional
}
```

**Response (201 Created):**
```json
{
    "message": "Group buy created successfully",
    "group_buy": {
        "id": 1,
        "product_id": 1,
        "product_name": "Product Name",
        "min_participants": 5,
        "current_participants": 0,
        "discount_percentage": 15.0,
        "unique_link": "abc123",
        "end_date": "2024-12-31T23:59:59",
        "status": "active"
    }
}
```

**Error Responses:**
```json
{
    "error": "Missing required field: product_id"
}
```
or
```json
{
    "error": "Discount percentage must be between 0 and 100"
}
```
or
```json
{
    "error": "Minimum participants must be at least 2"
}
```

### GET /groupbuy/<unique_link>
Get details of a specific group buy.

**Response (200 OK):**
```json
{
    "id": 1,
    "product_id": 123,
    "product_name": "Product Name",
    "min_participants": 5,
    "current_participants": 2,
    "discount_percentage": 15.0,
    "unique_link": "abc123",
    "end_date": "2024-12-31T23:59:59",
    "status": "active"
}
```

### POST /groupbuy/join/<unique_link>
Join an existing group buy.

**Response (200 OK):**
```json
{
    "message": "Joined group buy successfully",
    "current_participants": 3
}
```

### POST /groupbuy/apply-discount/<cart_id>
Apply group buy discount to cart.

**Request Body:**
```json
{
    "group_buy_id": 1
}
```

**Response (200 OK):**
```json
{
    "message": "Discount applied successfully",
    "original_price": 100.00,
    "discounted_price": 85.00,
    "discount_percentage": 15.0
}
```

## Features

- **Product Selection**: Choose from existing in-stock products
- **Customizable Discount**: Set your own discount percentage (0-100%)
- **Flexible Participation**: Set minimum number of participants (minimum 2)
- **Time Limit**: Optional end date for the group buy
- **Real-time Updates**: Track current number of participants
- **Unique Links**: Shareable links for each group buy
- **Status Tracking**: Monitor group buy status (active/expired/completed)

## Error Handling

- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Product or group buy not found
- `500 Internal Server Error`: Server-side error

## Example Usage

1. **Get Available Products:**
```bash
curl -X GET 'http://localhost:5000/groupbuy/products' \
  -H 'Authorization: Bearer your_token'
```

2. **Create Group Buy:**
```bash
curl -X POST 'http://localhost:5000/groupbuy/create' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_token' \
  -d '{
    "product_id": 1,
    "min_participants": 5,
    "discount_percentage": 15.0,
    "end_date": "2024-12-31T23:59:59"
  }'
```

3. **Join Group Buy:**
```bash
curl -X POST 'http://localhost:5000/groupbuy/join/abc123' \
  -H 'Authorization: Bearer your_token'
```

4. **Apply Discount:**
```bash
curl -X POST 'http://localhost:5000/groupbuy/apply-discount/1' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_token' \
  -d '{
    "group_buy_id": 1
  }'
```

---
# Cart Blueprint Documentation

This document provides detailed documentation for the Cart Blueprint of our e-commerce application. The Cart Blueprint manages all cart-related actions such as adding items, retrieving cart items, removing items, checking out, and applying coupons.

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Error Handling](#error-handling)
5. [Usage Examples](#usage-examples)

## Overview
The Cart Blueprint provides the following functionalities:
- Retrieve cart items with optional category filtering
- Add/update products in cart
- Remove products from cart
- Process checkout with optional credit application
- Apply discount coupons
- Manage stock levels automatically

## Authentication
All endpoints require user authentication using JWT tokens. Ensure your requests include the Authorization header with a valid JWT token.

All API endpoints are prefixed with: `/cart`

## Endpoints

### GET /cart
Retrieve items in the user's cart.

**Query Parameters:**
- `email` (required): User's email address

**Response (200 OK):**
```json
[
  {
    "cart_id": 1,
    "product_id": 123,
    "quantity": 2,
    "product_name": "Sample Product",
    "price": 29.99,
    "image_url": "https://example.com/image.jpg",
    "stock": 50
  }
]
```

**Error Responses:**
- 400 Bad Request: `{"error": "Email is required"}`
- 400 Bad Request: `{"error": "Invalid email"}`
- 500 Internal Server Error: `{"error": "Failed to retrieve cart", "message": "error details"}`

### POST /cart
Add a product to the cart. If the product already exists in the cart, the quantity will be increased by the specified amount.

**Request Body:**
```json
{
  "email": "user@example.com",
  "product_id": 123,
  "quantity": 1  // Optional, defaults to 1
}
```

**Response (200 OK):**
```json
{
  "message": "Product added to cart successfully",
  "cart_id": 1,
  "product_id": 123,
  "quantity": 2  // Total quantity after adding (includes existing quantity if product was already in cart)
}
```

**Error Responses:**
- 400 Bad Request: `{"error": "No JSON data provided"}`
- 400 Bad Request: `{"error": "product_id is required"}`
- 400 Bad Request: `{"error": "quantity must be a positive integer"}`
- 400 Bad Request: `{"error": "Invalid email"}`
- 400 Bad Request: `{"error": "Not enough stock available"}`
- 404 Not Found: `{"error": "Product not found"}`
- 500 Internal Server Error: `{"error": "Failed to add product to cart", "message": "error details"}`

### DELETE /cart/{cart_id}/products/{product_id}
Remove a product from the cart.

**Query Parameters:**
- `email` (required): User's email address

**Alternative: Request Body (if not using query parameters):**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Item removed from cart"
}
```

**Error Responses:**
- 400 Bad Request: `{"error": "Email is required"}`
- 400 Bad Request: `{"error": "Invalid email"}`
- 404 Not Found: `{"error": "Cart not found"}`
- 404 Not Found: `{"error": "Product not found in cart"}`
- 500 Internal Server Error: `{"error": "Failed to remove item from cart", "message": "error details"}`

### POST /cart/checkout
Checkout the cart and create an order.

**Request Body:**
```json
{
  "email": "user@example.com",
  "credits_to_apply": 0.0  // Optional
}
```

**Response (200 OK):**
```json
{
  "message": "Checkout successful",
  "final_total": 59.98,
  "credits_earned": 5.99,
  "remaining_credits": 10.00
}
```

**Error Responses:**
- 400 Bad Request: `{"error": "Invalid email"}`
- 400 Bad Request: `{"error": "Cart is empty"}`
- 400 Bad Request: `{"error": "Not enough credits"}`
- 400 Bad Request: `{"error": "Not enough stock for Product Name. Available: X"}`

### POST /cart/apply-coupon
Apply a coupon code to the cart.

**Request Body:**
```json
{
  "email": "user@example.com",
  "coupon_code": "P1Q8"
}
```

**Response (200 OK):**
```json
{
  "message": "Coupon applied successfully",
  "original_total": 100.00,
  "discount_percentage": 15,
  "discount_amount": 15.00,
  "new_total": 85.00
}
```

**Error Responses:**
- 400 Bad Request: `{"error": "Invalid email"}`
- 400 Bad Request: `{"error": "Invalid coupon code"}`
- 400 Bad Request: `{"error": "This coupon is expired"}`
- 400 Bad Request: `{"error": "This coupon has already been used"}`
- 400 Bad Request: `{"error": "Cart is empty"}`

## Error Handling
The API uses standard HTTP status codes:
- `400 Bad Request`: Invalid input, insufficient stock, or business rule violation
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Usage Examples

### 1. Get Cart Items with Category Filter
```bash
curl -X GET 'http://localhost:5000/cart?category=Electronics' \
  -H 'Authorization: Bearer your_token'
```

### 2. Add Item to Cart
```bash
curl -X POST 'http://localhost:5000/cart' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_token' \
  -d '{
    "product_id": 101,
    "quantity": 2,
    "email": "user@example.com"
  }'
```

### 3. Apply Coupon
```bash
curl -X POST 'http://localhost:5000/cart/apply-coupon' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_token' \
  -d '{
    "coupon_code": "P1Q8",
    "email": "user@example.com"
  }'
```

### 4. Checkout with Credits
```bash
curl -X POST 'http://localhost:5000/cart/checkout' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_token' \
  -d '{
    "credits_to_apply": 50.0,
    "email": "user@example.com"
  }'
```

---

*Note*: Make sure your server is running and that you have valid authentication tokens to access these endpoints.

---

# Home Route

All endpoints are prefixed with `/`
## Endpoints
### POST `/daily`
#### **Daily Login Reward**
- **URL**: `/daily`
- **Method**: POST
- **Description**: Record a daily login and calculate the login streak and reward.
- **Request Body**:
  ```json
  {
    "user_id": 1
  }
  ```

### GET `/home`
- **URL**: `/home`
- **Method**: GET
- **Description**: Returns all products in the database with optional category filtering.

**Query Parameters:**
- `category` (optional): Filter products by category ID (e.g., `/home?category=1` for Electronics)

#### Example Response
```json
[
    {
        "id": 1,
        "name": "Product 1",
        "description": "Description of Product 1",
        "price": 19.99,
        "stock": 100,
        "image_url": "http://example.com/image1.jpg",
        "seller_id": 1,
        "category_id": 1,
        "category_name": "Electronics",
        "created_at": "2023-10-01T12:00:00"
    },
    {
        "id": 2,
        "name": "Product 2",
        "description": "Description of Product 2",
        "price": 29.99,
        "stock": 50,
        "image_url": "http://example.com/image2.jpg",
        "seller_id": 2,
        "category_id": 2,
        "category_name": "Clothing",
        "created_at": "2023-09-25T10:00:00"
    }
]
```

**Error Response (500 Internal Server Error):**
```json
{
    "error": "Error message description"
}
```

**Example Usage:**
```bash
# Get all products
curl -X GET 'http://localhost:5000/home'

# Get products filtered by category (e.g., Electronics with category_id=1)
curl -X GET 'http://localhost:5000/home?category=1'
```

### GET `/categories`
- **URL**: `/categories`
- **Method**: GET
- **Description**: This endpoint returns a JSON response containing all categories

#### Example Response

```json
[
    {
        "id": 1,
        "name": "Product 1",
        "description": "Description of Product 1",
        "created_at": "2023-10-01T12:00:00"
    },
    {
        "id": 2,
        "name": "Product 2",
        "description": "Description of Product 2",
        "created_at": "2023-09-25T10:00:00"
    },
    ...
]
```

### GET `/latest`

- **URL**: `/latest`
- **Method**: GET
- **Description**: This endpoint returns a JSON response containing:
- **Featured Products**: The latest 5 products added to the database, ordered by their creation date.
- **Categories**: The top 5 categories in the database.
- **Best Sellers**: The top 5 best-selling products based on the number of times they have been ordered.

#### Example Response
```json
{
    "featured_products": [
        {
            "id": 1,
            "name": "Product 1",
            "description": "Description of Product 1",
            "price": 19.99,
            "stock": 100,
            "image_url": "http://example.com/image1.jpg",
            "seller_id": 1,
            "category_id": 1,
            "created_at": "2023-10-01T12:00:00"
        },
        ...
    ],
    "categories": [
        {
            "id": 1,
            "name": "Category 1",
            "description": "Description of Category 1"
        },
        ...
    ],
    "best_sellers": [
        {
            "id": 2,
            "name": "Product 2",
            "description": "Description of Product 2",
            "price": 29.99,
            "stock": 50,
            "image_url": "http://example.com/image2.jpg",
            "seller_id": 2,
            "category_id": 2,
            "created_at": "2023-09-25T10:00:00"
        },
        ...
    ]
}
```

### GET `/product/<product_id>`
- **URL**: `/product/<product_id>`
- **Method**: GET
- **Description**: Returns detailed information about a specific product.

**URL Parameters:**
- `product_id` (required): The ID of the product to retrieve

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Product Name",
    "description": "Detailed product description",
    "price": 99.99,
    "stock": 50,
    "image_url": "http://example.com/image.jpg",
    "seller_id": 1,
    "category_id": 1,
    "category_name": "Electronics",
    "created_at": "2023-10-01T12:00:00",
    "seller_name": "John Doe",
    "average_rating": 4.5,
    "review_count": 10
}
```

**Error Responses:**
- **404 Not Found:**
```json
{
    "error": "Product not found"
}
```
- **500 Internal Server Error:**
```json
{
    "error": "Error message description"
}
```

**Example Usage:**
```bash
# Get details for product with ID 1
curl -X GET 'http://localhost:5000/product/1'
```

### GET `/search`
Search for products with various filters and sorting options.

**Query Parameters:**
- `q` (optional): Search query string to match against product name and description
- `category` (optional): Filter by category ID
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `sort_by` (optional): Field to sort by (name, price, created_at). Default: name
- `order` (optional): Sort order (asc, desc). Default: asc
- `page` (optional): Page number for pagination. Default: 1
- `per_page` (optional): Number of items per page. Default: 10

**Response:**
```json
{
    "products": [
        {
            "id": 1,
            "name": "Product Name",
            "description": "Product Description",
            "price": 99.99,
            "stock": 50,
            "image_url": "http://example.com/image.jpg",
            "category_id": 1,
            "category_name": "Electronics",
            "created_at": "2024-03-15T10:30:00"
        }
    ],
    "total": 100,
    "pages": 10,
    "current_page": 1,
    "has_next": true,
    "has_prev": false
}
```

**Error Response:**
```json
{
    "error": "Failed to search products",
    "message": "Error details"
}
```

**Example Usage:**
```bash
# Basic search
curl -X GET 'http://localhost:5000/search?q=laptop'

# Search with filters
curl -X GET 'http://localhost:5000/search?q=laptop&category=1&min_price=500&max_price=1000'

# Search with sorting
curl -X GET 'http://localhost:5000/search?q=laptop&sort_by=price&order=desc'

# Search with pagination
curl -X GET 'http://localhost:5000/search?q=laptop&page=2&per_page=20'

# Complex search with all parameters
curl -X GET 'http://localhost:5000/search?q=laptop&category=1&min_price=500&max_price=1000&sort_by=price&order=desc&page=2&per_page=20'
```

**Features:**
- Full-text search in product name and description
- Category filtering
- Price range filtering
- Multiple sorting options
- Pagination support
- Case-insensitive search
- Flexible parameter combinations

**Notes:**
- All parameters are optional
- Search is case-insensitive
- Price filters accept decimal values
- Pagination starts from 1
- Maximum items per page is 100

# NEOMART E-commerce API Documentation

## Cart API

### Base URLs
- Production: https://ecommerceapi-production-48c7.up.railway.app/api
- Development: http://localhost:5000/api

### Endpoints

#### GET /cart
Retrieves all items in the user's cart.

**Query Parameters:**
- `email` (required): User's email address

**Response:**
```json
{
    "cart_items": [
        {
            "cart_id": 1,
            "product_id": 2,
            "quantity": 3,
            "product_name": "Example Product",
            "price": 29.99,
            "image_url": "https://example.com/image.jpg",
            "stock": 10
        }
    ]
}
```

#### POST /cart
Adds a product to the cart or updates the quantity if the product already exists.

**Request Body:**
```json
{
    "product_id": 2,
    "quantity": 1,
    "email": "user@example.com"
}
```

**Important Notes:**
- If the product already exists in the cart, the new quantity will be ADDED to the existing quantity
- The total quantity (existing + new) cannot exceed the product's available stock
- The response includes the TOTAL quantity after the addition
- All quantities must be positive integers

**Response:**
```json
{
    "message": "Product added to cart successfully",
    "cart_id": 1,
    "product_id": 2,
    "quantity": 3  // This is the total quantity after addition
}
```

**Error Responses:**
- 400: Invalid request (missing fields, invalid email, insufficient stock)
- 404: Product not found
- 500: Server error

#### DELETE /cart/{cart_id}/products/{product_id}
Removes a product from the cart.

**Query Parameters:**
- `email` (required): User's email address

**Response:**
```json
{
    "message": "Product removed from cart successfully"
}
```

#### POST /cart/checkout
Process checkout for the cart.

**Request Body:**
```json
{
    "email": "user@example.com",
    "credits_to_apply": 10.00  // Optional
}
```

**Response:**
```json
{
    "message": "Checkout successful",
    "order_id": 123,
    "total": 89.99
}
```

#### POST /cart/apply-coupon
Apply a coupon code to the cart.

**Request Body:**
```json
{
    "email": "user@example.com",
    "coupon_code": "SAVE20"
}
```

**Response:**
```json
{
    "message": "Coupon applied successfully",
    "discount": 20.00,
    "new_total": 79.99
}
```

### General Notes
- All monetary values are in USD
- Email verification is required for all cart operations
- Stock is checked in real-time for all cart operations
- Quantities must be positive integers
- The API will return appropriate error messages for any validation failures

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request`: Invalid input or business rule violation
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Common error response format:
```json
{
  "error": "Error message description"
}
```

## Authentication

All cart endpoints require user authentication using Flask-Login. Requests must include valid session credentials.

## Features

- **Product Management**: Add, remove, and update quantities of products in cart
- **Category Filtering**: Filter cart items by product category
- **Credit System**: Apply and earn credits during checkout
- **Coupon System**: Apply discount coupons to reduce total price
- **Stock Management**: Automatic stock validation and updates during checkout
- **Error Handling**: Comprehensive error checking and appropriate responses

## Dependencies

- Flask
- Flask-Login
- SQLAlchemy
- Python 3.x

# Order Management API

This API provides endpoints for users to view their order history and order details.

## Endpoints

### GET /orders
Get all orders for the current user.

**Response (200 OK):**
```json
[
    {
        "order_id": 1,
        "created_at": "2024-03-15T10:30:00",
        "total_amount": 149.99,
        "status": "completed",
        "items": [
            {
                "product_id": 1,
                "product_name": "Product Name",
                "quantity": 2,
                "price": 74.99,
                "image_url": "http://example.com/image.jpg"
            }
        ],
        "credits_used": 50.0,
        "credits_earned": 15
    }
]
```

### GET /orders/<order_id>
Get detailed information about a specific order.

**Response (200 OK):**
```json
{
    "order_id": 1,
    "created_at": "2024-03-15T10:30:00",
    "total_amount": 149.99,
    "status": "completed",
    "items": [
        {
            "product_id": 1,
            "product_name": "Product Name",
            "quantity": 2,
            "price": 74.99,
            "image_url": "http://example.com/image.jpg",
            "category": "Electronics"
        }
    ],
    "credits_used": 50.0,
    "credits_earned": 15,
    "shipping_address": "123 Main St, City, Country",
    "payment_method": "credit_card"
}
```

**Error Responses:**
- **404 Not Found:**
```json
{
    "error": "Order not found"
}
```- **500 Internal Server Error:**
```json
{
    "error": "Error message description"
}
```## Example Usage

1. **Get All Orders:**
```bash
curl -X GET 'http://localhost:5000/orders' \
  -H 'Authorization: Bearer your_token'
```

2. **Get Order Details:**
```bash
curl -X GET 'http://localhost:5000/orders/1' \
  -H 'Authorization: Bearer your_token'
```## Features

- **Order History**: View all past orders
- **Order Details**: Get detailed information about specific orders
- **Item Details**: View products purchased in each order
- **Credit Tracking**: See credits used and earned for each order
- **Status Tracking**: Monitor order status
- **Secure Access**: Only authenticated users can view their own orders

## Error Handling

- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Order not found or not owned by user
- `500 Internal Server Error`: Server-side error





