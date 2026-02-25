# REST API with Python Flask

A simple REST API built with Flask, SQLAlchemy, and Marshmallow.

## Features

- CRUD operations for User management
- SQLite database
- JSON serialization with Marshmallow
- Error handling
- Health check endpoint
- Unit tests

## Endpoints

- `GET /api/health` - Health check
- `GET /api/users` - Get all users
- `GET /api/users/<id>` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

## Installation