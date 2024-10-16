# Library Management System (LMS)

## Overview

The Library Management System (LMS) is designed to streamline and manage various library operations, enhancing the efficiency of the book borrowing and management process. This system incorporates distinct roles—Admin, Librarian, and Member—each with specific responsibilities and privileges.

## Key Features

### User Roles
- **Admin**: The administrator has complete control over the system, managing librarians, members, and overseeing all library functions.
  ![admin_dashboard](https://github.com/user-attachments/assets/6658305a-5726-4976-a1b7-0739733c4472)

- **Librarian**: Librarians handle day-to-day operations, including managing book inventories, processing member requests, and overseeing borrowing and returning activities.
  ![librarian_dashboard](https://github.com/user-attachments/assets/8db70e50-e5fd-4c18-90c6-843c862b9f66)

- **Member**: Members are the end-users who borrow books, make requests, and interact with library services.
  ![member_dashboard](https://github.com/user-attachments/assets/d5d21df2-8ea7-4da1-aba6-be5fef3e7a99)

### Book Management
The system maintains a detailed inventory of available books, including the book's name, author, ISBN, and category. It tracks how many copies are available, ensuring a seamless borrowing process.
![manage_books](https://github.com/user-attachments/assets/831c381c-a81a-4daa-9407-66e5c7007e46)

### Borrowing and Returning System
Members can borrow books, which are added to their cart. The system monitors the borrowing period, alerts members when books are due, and calculates fines for late returns.
![librarian_approve_request](https://github.com/user-attachments/assets/b9d14820-099f-44a8-bfce-47da388fccf4)

### Member Request System
Prospective librarians can submit requests to add members to the library. Admins approve these requests, adding new members to the system.
![member_adding_request](https://github.com/user-attachments/assets/367bbdb8-deb1-4c4f-9fc4-125f2c2ba5a0)
![member_req](https://github.com/user-attachments/assets/ccf4a085-fca6-413d-9f1b-0cf65f9cde62)

### Fine Calculation
To encourage timely returns, the system automatically calculates fines for overdue books, ensuring smooth circulation and availability of books for all members.
![fine](https://github.com/user-attachments/assets/04d4e8f7-37b0-4180-a37c-049aef79da11)

### Librarian-Member Interaction
A unique feature of this system is the communication platform that allows librarians to address member queries and requests. This improves user experience and adds a layer of customer service to library management.

## Scalability
This system is designed to be scalable, potentially serving schools, universities, or community libraries in India, where libraries play a crucial role in educational and cultural development.

## Models

### 1. CustomUser
- **Fields:**
    - `username`: Unique username for the user (max length: 15).
    - `first_name`, `last_name`: Personal details of the user (max length: 15).
    - `email`: Unique email for user authentication.
    - `plain_password`: Store the plaintext password for admin viewing only.
    - `user_type`: Integer indicating user role (Admin, Librarian, Member).
    - `profile_pic`: Optional profile picture upload.
    - `address`: User's address.
    - `contact_number`: User's contact information.
    - `groups`, `user_permissions`: Manage user permissions and groups.
- **Methods:**
    - `__str__()`: Returns the user's email for representation.

### 2. CustomUserManager
Custom user manager to handle user creation:
- **Methods:**
    - `_create_user()`: Handles the core user creation logic.
    - `create_user()`: Creates a standard user.
    - `create_superuser()`: Creates an admin user with elevated privileges.

### 3. Admin
- **Fields:**
    - `user`: One-to-one relationship with `CustomUser`, representing admin users.

### 4. Librarian
- **Fields:**
    - `user`: One-to-one relationship with `CustomUser`, representing librarian users.

### 5. Member
- **Fields:**
    - `user`: One-to-one relationship with `CustomUser`, representing members.

### 6. MemberRequest
- **Fields:**
    - `librarian`: Foreign key to the `Librarian` model for managing member requests.
    - `username`, `email`, `password`: Details for new member registration.
    - `approved`: Boolean indicating if the request has been approved.
    - `created_at`: Timestamp for request creation.
- **Methods:**
    - `approve()`: Approves the member request and creates a new `CustomUser` and `Member`.

### 7. Book
- **Fields:**
    - `img`: Optional book cover image.
    - `name`: Name of the book (max length: 100).
    - `isbn`: Unique ISBN for the book (max length: 13).
    - `author`: Author of the book (max length: 100).
    - `category`: Book category (Education, Entertainment, etc.).
    - `copies_available`: Number of copies available for borrowing.
- **Methods:**
    - `__str__()`: Returns a string representation of the book name and ISBN.

### 8. CartList
![library_cart](https://github.com/user-attachments/assets/58ab37b8-aa5e-4b7d-b695-14c73a551745)

- **Fields:**
    - `user`: One-to-one relationship with `CustomUser`.
    - `cart_id`: Unique identifier for the cart.
    - `date_added`: Timestamp for when the cart was created.
- **Methods:**
    - `__str__()`: Returns the cart ID.

### 9. Item
- **Fields:**
    - `book`: Foreign key to the `Book` model.
    - `cart`: Foreign key to the `CartList` model.
    - `book_qty`: Quantity of the book added to the cart.
- **Methods:**
    - `clean()`: Validates that no more than 2 copies of a book can be added to the cart.
    - `__str__()`: Returns the book representation.

### 10. BorrowRecord
![member_borrow_record](https://github.com/user-attachments/assets/3198b250-66be-4819-96bd-21d2c1fd9c87)

- **Fields:**
    - `book`: Foreign key to the `Book` model.
    - `member`: Foreign key to the `CustomUser` model, limited to Members.
    - `borrowed_on`: Timestamp for when the book was borrowed.
    - `due_date`: The date the book is due for return.
    - `returned_on`: Timestamp for when the book was returned.
    - `status`: Current status of the borrow request (Pending Approval, Borrowed, etc.).
    - `return_approved`: Boolean indicating if the return has been approved.
    - `fine`: Monetary fine for late returns.
- **Methods:**
    - `return_book()`: Marks the book as returned and updates available copies.
    - `approve()`: Approves the borrow request and decreases book availability.
    - `calculate_fine()`: Calculates the fine if the book is returned late.

### 11. LibrarianMemberRequest
- **Fields:**
    - `profile_pic`: Optional profile picture upload for the member.
    - `first_name`, `last_name`, `email`, `username`, `address`, `password`, `contact_number`: Member details.
    - `requested_by`: Foreign key to `CustomUser`, indicating the librarian who requested the member creation.
    - `is_approved`: Boolean indicating if the request has been approved.
