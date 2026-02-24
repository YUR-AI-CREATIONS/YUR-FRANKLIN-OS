# User Management REST API

A Flask-based REST API for user management with JWT authentication.

## Features

- User registration and authentication
- JWT token-based authorization
- CRUD operations for users
- Profile management
- Input validation
- Pagination support
- Soft delete (deactivation)

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login user

### User Management (Requires Authentication)
- `GET /api/users` - Get all users (paginated)
- `GET /api/users/<id>` - Get specific user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user (soft delete)

### Profile Management (Requires Authentication)
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update current user profile

## Setup

1. Install dependencies: