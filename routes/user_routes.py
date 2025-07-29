"""
User routes with proper dependency injection and service layer usage
Demonstrates clean separation between web layer and business logic
"""
from flask import Blueprint, request, jsonify, g
from models.user import User
from utils.validators import UserValidator
from services.auth_service import AuthService
from services.jwt_service import token_required, optional_token
from core.container import container
import os

def debug_print(message):
    """Print debug message only if not in testing mode"""
    if not os.getenv('TESTING'):
        print(message)

user_bp = Blueprint('users', __name__)

# Dependency injection - get services from container
def get_user_service():
    """Get user service from dependency injection container"""
    return container.user_service()

@user_bp.route('/users', methods=['GET'])
@optional_token
def get_all_users():
    """Get all users. Authentication is optional for this endpoint."""
    try:
        user_service = get_user_service()
        users = user_service.list_users()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        debug_print(f"Error in get_all_users: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        user_service = get_user_service()
        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify(user.to_dict())
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        debug_print(f"Error in get_user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Get current user's profile. Requires JWT authentication.
    Demonstrates protected route functionality.
    """
    current_user = g.current_user
    return jsonify({
        "message": "Profile retrieved successfully",
        "user": current_user.to_dict(),
        "authenticated": True
    })

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user with the provided data.
    Uses dependency injection and service layer for business logic.
    """
    try:
        # Step 1: Get and validate JSON data
        data = request.get_json()
        debug_print(f"DEBUG: Received data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Step 2: Use service layer for user creation
        user_service = get_user_service()
        result = user_service.create_user(data)
        
        debug_print(f"DEBUG: Service result: {result}")
        
        # Step 3: Handle service response
        if result.get("success"):
            return jsonify({
                "message": "User created successfully", 
                "user": result["user"]
            }), 201
        else:
            return jsonify({"error": result.get("error", "Failed to create user")}), 400
    
    except Exception as e:
        debug_print(f"DEBUG: Unexpected error caught: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user using service layer"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_service = get_user_service()
        result = user_service.update_user(user_id, data)
        
        if result.get("success"):
            return jsonify({
                "message": "User updated successfully", 
                "user": result["user"]
            })
        else:
            status_code = 404 if "not found" in result.get("error", "").lower() else 400
            return jsonify({"error": result.get("error", "Failed to update user")}), status_code
    
    except Exception as e:
        debug_print(f"Error in update_user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user using service layer"""
    try:
        user_service = get_user_service()
        result = user_service.delete_user(user_id)
        
        if result.get("success"):
            return jsonify({"message": result.get("message", "User deleted successfully")})
        else:
            status_code = 404 if "not found" in result.get("error", "").lower() else 400
            return jsonify({"error": result.get("error", "Failed to delete user")}), status_code
    
    except Exception as e:
        debug_print(f"Error in delete_user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/search', methods=['GET'])
def search_users():
    """Search users using service layer"""
    try:
        query = request.args.get('name', '').strip()
        if not query:
            return jsonify({"error": "Please provide a name to search"}), 400
        
        user_service = get_user_service()
        users = user_service.search_users(query)
        return jsonify([user.to_dict() for user in users])
    
    except Exception as e:
        debug_print(f"Error in search_users: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500