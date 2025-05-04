import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from bs4 import BeautifulSoup

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword",
    )


@pytest.mark.django_db
def test_login_view(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_view(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
    data = {
        "csrfmiddlewaretoken": csrf_token,
        "username": "testuser1",
        "email": "testuser2@gmail.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "superpassword2468",
        "re_password": "superpassword2468",
    }
    url = reverse("register")
    response = client.post(url, data)
    assert response.status_code == 302
    new_user = User.objects.get(email="sovuh2703@gmail.com")
    assert new_user is not None


@pytest.mark.django_db
def test_profile_view_authenticated(client, user):
    user.is_active = True
    user.save()
    client.login(username="testuser", password="testpassword")
    response = client.get(reverse("profile"))
    assert response.status_code == 200
    user.is_active = False
    user.save()


@pytest.mark.django_db
def test_profile_view_not_authenticated(client):
    response = client.get(reverse("profile"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_is_not_active(user):
    assert user.is_active is False


@pytest.mark.django_db
def test_activate_user(client, user):
    token = str(AccessToken.for_user(user))
    assert user.is_active is False
    url = f"/activate/{user.id}/{token}/"
    response = client.get(url)
    user.refresh_from_db()
    assert user.is_active is True
    assert response.status_code == 200
