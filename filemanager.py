import json

USERS_FILE = "data/users.json"

def setup_storage():
 with open(USERS_FILE, 'w') as f:
  json.dump({}, f)

def load_data():
 with open(USERS_FILE, 'r') as f:
  return json.load(f)

def save_data(data):
 with open(USERS_FILE, 'w') as f:
  json.dump(data, f)
