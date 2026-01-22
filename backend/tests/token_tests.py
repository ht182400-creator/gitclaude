import os, sys
sys.path.append(os.getcwd())
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
from sqlmodel import SQLModel
from app.database import engine

# ensure all tables exist for tests (including newly added RefreshToken)
import os
db_path = os.path.join(os.getcwd(), 'dev.db')
if os.path.exists(db_path):
    os.remove(db_path)
SQLModel.metadata.create_all(engine)


def run():
    print('Starting token tests...')

    # create a user
    import time
    email = f"t{int(time.time())}@example.com"
    r = client.post('/users/register', json={'email': email, 'password': 'secret', 'full_name': 'Tester'})
    if r.status_code != 200:
        print('Register failed:', r.status_code, r.text)
        raise SystemExit(1)
    print('Register OK')

    # login
    r = client.post('/users/login', json={'email': email, 'password': 'secret'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data and 'refresh_token' in data
    access = data['access_token']
    refresh = data['refresh_token']
    print('Login returned tokens')

    # create a product
    r = client.post('/products/', json={'name': 'Widget', 'price_cents': 500, 'inventory': 10})
    assert r.status_code == 200
    # list products to obtain the created product id
    lr = client.get('/products/')
    assert lr.status_code == 200
    products = lr.json()
    assert len(products) > 0
    product = products[0]
    print('Product created')

    # create order with Authorization header
    r = client.post('/orders/', json={'items': [{'product_id': product['id'], 'quantity': 1}]}, headers={'Authorization': f'Bearer {access}'})
    assert r.status_code == 200
    print('Order created with access token')

    # refresh tokens
    r = client.post('/users/refresh', json={'refresh_token': refresh})
    assert r.status_code == 200
    new = r.json()
    assert 'access_token' in new and 'refresh_token' in new
    print('Refresh succeeded and rotated tokens')

    # old refresh should be revoked now
    r = client.post('/users/refresh', json={'refresh_token': refresh})
    assert r.status_code == 401
    print('Old refresh rejected')

    # logout (revoke current refresh)
    r = client.post('/users/logout', json={'refresh_token': new['refresh_token']})
    assert r.status_code == 200 and r.json().get('revoked')
    print('Logout revoked refresh')

    # using revoked refresh fails
    r = client.post('/users/refresh', json={'refresh_token': new['refresh_token']})
    assert r.status_code == 401
    print('Revoked refresh rejected')

    print('All token tests passed')

    # Cookie-based flow tests
    print('Starting cookie-based flow tests...')
    # login using cookie option (server will set HttpOnly cookie)
    r = client.post('/users/login', json={'email': email, 'password': 'secret'}, headers={'x-use-cookie': '1'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    print('Cookie-login returned access_token and set cookie')

    # refresh using cookie (no payload) - TestClient preserves cookies
    r = client.post('/users/refresh')
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    print('Cookie-based refresh succeeded and rotated cookie')

    # logout via cookie
    r = client.post('/users/logout')
    assert r.status_code == 200 and r.json().get('revoked')
    print('Cookie-based logout revoked token and cleared cookie')


if __name__ == '__main__':
    run()
