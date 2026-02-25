import requests
import json

# Base URL for the API
BASE_URL = 'http://localhost:5000'

def test_create_todo():
    """Test creating a new todo"""
    data = {
        'title': 'Test Todo',
        'description': 'This is a test todo item',
        'completed': False
    }
    response = requests.post(f'{BASE_URL}/todos', json=data)
    print(f"Create Todo: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()['id']

def test_get_todos():
    """Test getting all todos"""
    response = requests.get(f'{BASE_URL}/todos')
    print(f"\nGet All Todos: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_get_todo(todo_id):
    """Test getting a specific todo"""
    response = requests.get(f'{BASE_URL}/todos/{todo_id}')
    print(f"\nGet Todo {todo_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_update_todo(todo_id):
    """Test updating a todo"""
    data = {
        'title': 'Updated Test Todo',
        'description': 'This todo has been updated',
        'completed': True
    }
    response = requests.put(f'{BASE_URL}/todos/{todo_id}', json=data)
    print(f"\nUpdate Todo {todo_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_toggle_todo(todo_id):
    """Test toggling todo completion"""
    response = requests.patch(f'{BASE_URL}/todos/{todo_id}/toggle')
    print(f"\nToggle Todo {todo_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_delete_todo(todo_id):
    """Test deleting a todo"""
    response = requests.delete(f'{BASE_URL}/todos/{todo_id}')
    print(f"\nDelete Todo {todo_id}: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    print("Testing Todo API...")
    
    # Create a todo
    todo_id = test_create_todo()
    
    # Get all todos
    test_get_todos()
    
    # Get specific todo
    test_get_todo(todo_id)
    
    # Update todo
    test_update_todo(todo_id)
    
    # Toggle todo
    test_toggle_todo(todo_id)
    
    # Delete todo
    test_delete_todo(todo_id)
    
    print("\nAPI testing completed!")