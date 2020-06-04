import os

aws = {
    'region': os.environ['AWS_REGION_'],
    'access_key_id': os.environ['AWS_ACCESS_KEY_ID_'],
    'secret_access_key': os.environ['AWS_SECRET_KEY_'],
}

app_url = os.environ['APP_URL'] + '{}'
