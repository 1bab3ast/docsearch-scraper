import os

api_key_prod = os.environ.get('API_KEY_PROD', '')

slack_hook = os.environ.get('SLACK_HOOK', '')


def confirm(message="Confirm"):
    from builtins import input

    prompt = message + ' [y/n]:\n'

    while True:
        ans = input(prompt)

        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue

        if ans in ['y', 'Y']:
            return True

        if ans in ['n', 'N']:
            return False


def get_user_value(message):
    from builtins import input

    prompt = message
    return input(prompt)


def make_custom_get_request(url):
    import requests

    return requests.get(url)


def make_request(endpoint, type=None, data=None, username=None, password=None,
                 json_request=False):
    import requests

    if "://" not in endpoint:
        print(f"Wrong endpoint:{endpoint}, it should be a complete URL")
        exit(6)

    if username is None or password is None:
        print(f"{endpoint}: both username and password must be set")
        exit(7)

    if data and not isinstance(data, dict):
        raise ValueError(f"{data} must be a dict ")

    if type == 'POST':
        if json_request:
            r = requests.post(endpoint,
                              auth=(username, password),
                              json=data)
        else:
            r = requests.post(endpoint,
                              auth=(username, password),
                              data=data)

        if r.status_code // 100 != 2:
            print(f'ISSUE for POST request : {endpoint} with params: {data}')
            print(r.text)
        return r

    if type == 'DELETE':
        r = requests.delete(endpoint,
                            auth=(username, password))

        success_codes = [200, 201, 204]

        if r.status_code not in success_codes:
            print(f'ISSUE for DELETE request : {endpoint} with params: {data}')
        return r

    if type == 'PUT':
        r = requests.put(endpoint,
                         auth=(username, password),
                         data=data)
        print(r.status_code)
        if r.status_code // 100 != 2:
            print(f'ISSUE for PUT request : {endpoint} with params: {data}')
        return r

    if data is None:
        r = requests.get(endpoint,
                         auth=(username, password))

    else:
        r = requests.get(endpoint,
                         auth=(username, password),
                         params=data)
    if r.status_code // 100 != 2:
        print(f'ISSUE for GET request : {endpoint} with params: {data}')

    if json_request:
        r.json()

    return r.text


def send_slack_notif(reports):
    if slack_hook == '':
        raise ValueError("NO SLACK_HOOK")

    from slacker import Slacker

    slack = Slacker(None, slack_hook)

    slack.incomingwebhook.post({
        "text": "",
        "channel": "#notif-docsearch",
        "username": "Deployer",
        "icon_emoji": ":rocket:",
        "attachments": reports
    })


def check_output_decoded(command, cwd=None):
    from subprocess import check_output
    return check_output(command, cwd=cwd).decode()
