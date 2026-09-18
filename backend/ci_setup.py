import asyncio
import os
import time

import requests


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
API = f"{BASE_URL}/api"

TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "Wavygo@2026")

FOUNDER_EMAIL = os.environ.get("FOUNDER_EMAIL", "founder@wavygo.in")
FOUNDER_PASSWORD = os.environ.get("FOUNDER_PASSWORD", TEST_PASSWORD)

TEST_USERS = [
    {
        "email": os.environ.get("ADMIN_EMAIL", "admin@wavygo.in"),
        "name": "CI Admin",
        "role": "Admin",
    },
    {
        "email": os.environ.get("MANAGER_EMAIL", "manager@wavygo.in"),
        "name": "CI Manager",
        "role": "Manager",
    },
    {
        "email": os.environ.get("EMPLOYEE_EMAIL", "employee@wavygo.in"),
        "name": "CI Employee",
        "role": "Employee",
    },
    {
        "email": os.environ.get("INTERN_EMAIL", "intern@wavygo.in"),
        "name": "CI Intern",
        "role": "Intern",
    },
]


def wait_for_backend():
    for _ in range(60):
        try:
            response = requests.get(f"{API}/health", timeout=2)
            if response.status_code == 200:
                print("Backend is ready.")
                return
        except requests.RequestException:
            pass

        time.sleep(1)

    raise RuntimeError("Backend did not become ready.")


def login(email, password):
    response = requests.post(
        f"{API}/auth/login",
        json={
            "email": email,
            "password": password,
            "remember": True,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def register_user(token, user):
    response = requests.post(
        f"{API}/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": user["email"],
            "password": TEST_PASSWORD,
            "name": user["name"],
            "role": user["role"],
        },
        timeout=10,
    )

    if response.status_code == 409:
        print(f"{user['role']} already exists: {user['email']}")
        return

    response.raise_for_status()
    print(f"Created CI {user['role']}: {user['email']}")


async def seed_part2():
    from seed_part2 import seed_part2 as run_seed_part2

    await run_seed_part2()
    print("Part 2 CI seed completed.")


def main():
    wait_for_backend()

    founder = login(FOUNDER_EMAIL, FOUNDER_PASSWORD)
    founder_token = founder["access_token"]

    # Founder creates the Admin first.
    admin = TEST_USERS[0]
    register_user(founder_token, admin)

    # Log in as the CI Admin.
    admin_login = login(admin["email"], TEST_PASSWORD)
    admin_token = admin_login["access_token"]

    # Admin creates the remaining non-Founder users.
    for user in TEST_USERS[1:]:
        register_user(admin_token, user)

    asyncio.run(seed_part2())

    print("CI environment setup completed successfully.")


if __name__ == "__main__":
    main()