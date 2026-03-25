users = [{"name": "Alice", "active": True}, {"name": "Bob", "active": False}, {"name": "John", "active": True}]
for u in users:
    if u["active"]:
        print(f"{u['name']} is online!")