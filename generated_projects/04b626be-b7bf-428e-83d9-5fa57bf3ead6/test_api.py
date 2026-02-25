import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_todo_api():
    """Test all todo API endpoints"""
    
    print("Testing Todo API...")
    
    # Test 1: Get all todos (should be empty initially)
    print("\n1. Getting all todos...")
    response = requests.get(f'{BASE_URL}/todos')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Create a new todo
    print("\n2. Creating a new todo...")
    new_todo = {
        'title': 'Learn Python',
        'description': 'Complete Python tutorial',
        'completed': False
    }
    response = requests.post(f'{BASE_URL}/todos', json=new_todo)
    print(f"Status: {response.status_code}")
    created_todo = response.json()
    print(f"Response: {created_todo}")
    todo_id = created_todo['id']
    
    # Test 3: Get specific todo
    print(f"\n3. Getting todo with ID {todo_id}...")
    response = requests.get(f'{BASE_URL}/todos/{todo_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Update todo
    print(f"\n4. Updating todo with ID {todo_id}...")
    update_data = {
        'title': 'Learn Python (Updated)',
        'description': 'Complete advanced Python tutorial',
        'completed': True
    }
    response = requests.put(f'{BASE_URL}/todos/{todo_id}', json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 5: Toggle todo completion
    print(f"\n5. Toggling todo completion for ID {todo_id}...")
    response = requests.patch(f'{BASE_URL}/todos/{todo_id}/toggle')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 6: Create another todo
    print("\n6. Creating another todo...")
    another_todo = {
        'title': 'Build API',
        'description': 'Create a REST API with Flask'
    }
    response = requests.post(f'{BASE_URL}/todos', json=another_todo)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 7: Get all todos again
    print("\n7. Getting all todos...")
    response = requests.get(f'{BASE_URL}/todos')
    print(f"Status: {response.status_code}")
    all_todos = response.json()
    print(f"Response: {all_todos}")
    
    # Test 8: Delete a todo
    print(f"\n8. Deleting todo with ID {todo_id}...")
    response = requests.delete(f'{BASE_URL}/todos/{todo_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 9: Try to get deleted todo (should return 404)
    print(f"\n9. Trying to get deleted todo with ID {todo_id}...")
    response = requests.get(f'{BASE_URL}/todos/{todo_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == '__main__':
    test_todo_api()