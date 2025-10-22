# FastAPI E-commerce Project

A FastAPI-based backend for an e-commerce application.  
This project includes product management, user authentication (login/register), JWT token authentication, and secure HttpOnly cookies.

---

## Features

- **User Authentication**  
  - Register new users  
  - Login using username/password  
  - JWT authentication  
  - HttpOnly cookie support

- **Product Management**  
  - Add products with details like name, description, price, stock, rating, images, etc.  
  - Fetch products and view details

- **Database**  
  - MySQL used as backend database  
  - SQLAlchemy ORM for database interactions

- **Security**  
  - Passwords hashed with bcrypt  
  - Tokens stored in HttpOnly cookies (cannot be accessed by JavaScript)

---

## Project Structure

fastapi-ecommerce/
│
├── app/
│ ├── main.py # FastAPI application entry point
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── database.py # Database connection
│ ├── auth.py # Authentication routes (login/register)
│ └── products.py # Product routes
│
├── env/ # Virtual environment (ignored in Git)
├── requirements.txt # Python dependencies
├── .gitignore # Files/folders to ignore
└── README.md

yaml
Copy code

---

## Prerequisites

- Python 3.12+
- MySQL server
- Node.js (if frontend is included)

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/fastapi-ecommerce.git
cd fastapi-ecommerce
Create virtual environment

bash
Copy code
python -m venv env
Activate virtual environment

Windows:

bash
Copy code
.\env\Scripts\activate
Linux/macOS:

bash
Copy code
source env/bin/activate
Install dependencies

bash
Copy code
pip install -r requirements.txt
Configure database
Update database.py with your MySQL credentials:

python
Copy code
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"
Run the server

bash
Copy code
uvicorn app.main:app --reload
Server will start at:

cpp
Copy code
http://127.0.0.1:8000
API Endpoints
Auth
Method	Endpoint	Description
POST	/register	Register a new user
POST	/login	Login user and set token
GET	/me	Get current user info

Products
Method	Endpoint	Description
POST	/products	Add a new product
GET	/products	Fetch all products
GET	/products/{id}	Fetch single product by id

How to Test with Postman
Register a user

Method: POST

URL: http://127.0.0.1:8000/register

Body: x-www-form-urlencoded

makefile
Copy code
username: yourusername
password: yourpassword
Login a user

Method: POST

URL: http://127.0.0.1:8000/login

Body: x-www-form-urlencoded

makefile
Copy code
username: yourusername
password: yourpassword
Make sure Send Cookies is enabled to receive HttpOnly cookie.

Get current user info

Method: GET

URL: http://127.0.0.1:8000/me

Make sure the cookie access_token from login is included.

Notes
Passwords are hashed with bcrypt (passlib).

Tokens are stored in HttpOnly cookies for security.

Configure CORS for frontend integration (FastAPI CORSMiddleware).

License
This project is licensed under the MIT License.

yaml
Copy code

---

If you want, I can also **write a short GitHub push guide** for this project to add to the README so anyone can clone and contribute.  

Do you want me to add that too?
