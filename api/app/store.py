"""In-memory data for the sample application."""

users: dict[str, dict[str, str]] = {}
orders: dict[str, dict[str, str]] = {}
reset_tokens: dict[str, str] = {}


def seed() -> None:
    """Reset the store and create demo accounts."""
    from app.auth import hash_password

    users.clear()
    orders.clear()
    reset_tokens.clear()

    for user_id, email, role, name in (
        ("customer-1", "alice@example.com", "customer", "Alice"),
        ("customer-2", "bob@example.com", "customer", "Bob"),
        ("staff-1", "staff@example.com", "staff", "Sam"),
    ):
        users[user_id] = {
            "id": user_id,
            "email": email,
            "password_hash": hash_password("demo-password"),
            "role": role,
            "name": name,
        }
