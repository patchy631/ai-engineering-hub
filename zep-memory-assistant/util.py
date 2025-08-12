import re


def generate_user_id(first_name, last_name):
    """Generates a consistent user ID from first and last name."""
    user_id = re.sub(r"\W+", "", (first_name + last_name).lower())
    return user_id if user_id else "default_user"
