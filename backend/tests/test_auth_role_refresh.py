import uuid

API = "/api"


def test_role_change_takes_effect_for_an_existing_session(session_factory, admin_session, create_verified_user):
    email = f"role_refresh_{uuid.uuid4().hex[:8]}@example.com"
    user_session = session_factory()
    registered = create_verified_user(user_session, email, name="Role refresh regression")
    assert registered.status_code == 202

    user_id = next(user["id"] for user in admin_session.get(f"{API}/users").json() if user["email"] == email)
    promote = admin_session.put(f"{API}/users/{user_id}/role", json={"role": "editor"})
    assert promote.status_code == 200
    assert user_session.get(f"{API}/auth/me").json()["role"] == "editor"

    created_track = user_session.post(f"{API}/tracks", json={"title": "Role refresh track"})
    assert created_track.status_code == 200
    track_id = created_track.json()["id"]
    admin_session.delete(f"{API}/tracks/{track_id}")

    demote = admin_session.put(f"{API}/users/{user_id}/role", json={"role": "student"})
    assert demote.status_code == 200
    assert user_session.get(f"{API}/auth/me").json()["role"] == "student"
    denied = user_session.post(f"{API}/tracks", json={"title": "Must remain forbidden"})
    assert denied.status_code == 403

