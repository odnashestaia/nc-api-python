def test_users_and_user(managers):
    users = managers["users"]
    lst = users.get_users()
    assert "admin" in lst

    u = users.get_user(username="admin")
    assert u.get("id") == "admin"
