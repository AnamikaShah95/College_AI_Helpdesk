import hashlib

DEMO_USERS = [
    {
        "identifier": "student001",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "name": "Demo Student",
        "role": "student",
        "department": "CSE-AI",
        "semester": "V",
        "section": "Alpha",
        "student_id": "STU001",
    },
    {
        "identifier": "faculty001",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "name": "Demo Faculty",
        "role": "faculty",
        "department": "CSE-AI",
        "faculty_id": "FAC001",
    },
    {
        "identifier": "staff001",
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "name": "Demo Staff",
        "role": "staff",
        "department": "Academic Office",
        "staff_id": "STAFF001",
    },
]

def authenticate(identifier, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    for user in DEMO_USERS:
        if user["identifier"] == identifier and user["password_hash"] == hashed:
            return {k: v for k, v in user.items() if k != "password_hash"}
    return None

def get_demo_users():
    return [
        {"identifier": u["identifier"], "role": u["role"]}
        for u in DEMO_USERS
    ]
