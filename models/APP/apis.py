from app import *
from etc.config.externalLib import *
from models.APP import forms, users, apis
from models.FHE import FHE_Client, FHE_Integer

headers = {"Content-type":'application/json', "Authorization": None}

# Check server availbility
def connect_server(ip, port):
    url = 'http://' + str(ip) + ":" + str(port) + "/status/"
    r = requests.get(url, timeout=3)
    if r.status_code == 200:
        return True
    else:
        return False

# Get headers, cookies using arbitrary username and password
def create_session():
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    uuid0 = uuid.uuid4()
    password = os.urandom(8)
    # SIGNUP
    body = {'username': str(uuid0), 'password1': str(password), 'password2': str(password)}
    r = requests.post(url_prefix + "/api/auth/signup/" , data=body)
    session['device-token'] = r.json()["token"]
    session['django-cookie'] = r.cookies.get_dict()
    # GET JWT PAIR
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']
    session['server_id'] = session['django-cookie']['sessionid']

# Post encrypted integer data
def create_data(x0, q0):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    x0_e = base64.b64encode(x0.to_bytes(math.ceil(x0.bit_length()/8),'big')).decode()
    q0_e = base64.b64encode(q0.to_bytes(math.ceil(q0.bit_length()/8),'big')).decode()
    body= {"integers":[{"index":0, "X":str(x0_e), "q":str(q0_e)}]}
    r = requests.post(url_prefix + '/integers/set/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    return r.json()['set_id']

# Delete integer data from server
def delete_data(id):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body = {"set_id": id}
    r = requests.delete(url_prefix + '/integers/set/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    if r.status_code == 200:
        return True
    else:
        return False

# Send the parsed equation with server_set_ids
def create_eval(id_str):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body= {"equation": str(id_str)}
    r = requests.post(url_prefix + '/integers/operation/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    return r.json()['setCreated']

# Get x_prime from server
def get_encrypted(id):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body = {"set_id": id}
    r = requests.get(url_prefix + '/integers/set/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    xp = r.json()['integers'][0].get("X")
    dec = int.from_bytes(base64.b64decode(xp), byteorder='big')
    return dec

# Get the entire set string from server for data storage when user requests
def get_server_int(id):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body = {"set_id": id}
    r = requests.get(url_prefix + '/integers/set/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    return r.json()

# Delete session from server
def delete_session(id):
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body = {"session_id": id}
    r = requests.delete(url_prefix + '/integers/session/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
    if r.status_code == 200:
        return True
    else:
        return False

# Upload session data to the server
def upload_session(integer_set):
    # Get JWT Access Token
    url_prefix = 'http://' + str(session['ip']) + ":" + str(session['port'])
    headers['Authorization'] = "Token " + session['device-token']
    r = requests.get(url_prefix + '/api/jwt/', headers=headers, timeout=3)
    session['access-token'] = r.json()['access']

    headers['Authorization'] = "Bearer " + session['access-token']
    body = {"session_id": session['server_id'],
            "integer_sets": integer_set}
    r = requests.post(url_prefix + '/integers/session/', json=body, headers=headers, cookies=session['django-cookie'], timeout=3)
