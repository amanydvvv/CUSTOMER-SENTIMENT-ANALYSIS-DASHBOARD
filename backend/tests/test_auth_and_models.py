import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import hash_password, verify_password, create_access_token, decode_token
from app.ml.preprocessing import clean_text

client = TestClient(app)


def test_password_hashing():
    pwd = "secretpassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    data = {"sub": "analyst_user", "role": "analyst"}
    token = create_access_token(data)
    assert isinstance(token, str)
    decoded = decode_token(token)
    assert decoded["sub"] == "analyst_user"
    assert decoded["role"] == "analyst"


def test_auth_register_and_login():
    import uuid
    unique_user = f"user_{uuid.uuid4().hex[:8]}"
    
    # 1. Register
    reg_payload = {"username": unique_user, "password": "Password@123", "role": "analyst"}
    r = client.post("/auth/register", json=reg_payload)
    assert r.status_code == 201
    res_data = r.json()
    assert res_data["username"] == unique_user
    assert res_data["role"] == "analyst"

    # 2. Login
    login_payload = {"username": unique_user, "password": "Password@123"}
    r_login = client.post("/auth/login", json=login_payload)
    assert r_login.status_code == 200
    token_data = r_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Test /auth/me with token
    r_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    assert r_me.json()["username"] == unique_user


def test_health_check_extended():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["database"] == "connected"
    assert "distilbert" in data
    assert "keybert_available" in data
    assert "all_models_loaded" in data


def test_models_list_endpoint():
    r = client.get("/models")
    assert r.status_code == 200
    models = r.json()
    assert "distilbert" in models
    assert "balanced_logistic_regression" in models
    assert "linearsvc" in models
