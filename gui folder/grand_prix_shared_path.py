import os

SHARED_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared_data")

if not os.path.exists(SHARED_DATA_PATH):
    os.makedirs(SHARED_DATA_PATH)