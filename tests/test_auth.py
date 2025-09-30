from http import HTTPStatus


def test_get_access_token_successfully(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_access_token_with_invalid_email(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'invalid@email.com',
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_access_token_with_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'invalid_password',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
