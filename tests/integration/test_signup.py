import pytest
from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_signup_and_duplicate_validation(client, django_user_model):
    url = reverse("signup")
    assert client.get(url).status_code == 200
    data = {
        "username": "new-synthetic-user",
        "password1": "complex-synthetic-2026",
        "password2": "complex-synthetic-2026",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert django_user_model.objects.get(username=data["username"]).is_staff is False
    assert client.get(url).url == reverse("stores:list")
    client.logout()
    assert client.post(url, data).context["form"].errors
    assert (
        client.post(url, data | {"username": "another", "password2": "wrong"})
        .context["form"]
        .errors
    )
