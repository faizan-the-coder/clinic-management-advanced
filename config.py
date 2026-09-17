import os
# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('DB_PASSWORD', '1234'),  # Update with your MySQL password
    'database': 'clinic_management',
    'charset': 'utf8mb4'
}

# UI Configuration
UI_COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'success': '#F18F01',      # Orange
    'background': '#F5F5F5',   # Light Gray
    'card': '#FFFFFF',         # White
    'text': '#333333',         # Dark Gray
    'text_secondary': '#666666',
    'border': '#E0E0E0',       # Light Border
    'hover': '#1E5A73',        # Dark Blue
    'danger': '#E74C3C',        # Red
    'warning':'#FFC107'         #amber/yellow
}

