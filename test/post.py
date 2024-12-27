import requests
import random
import string

# Endpoint URL
API_URL = "http://backend.example.in/colleges"  # Update with your actual endpoint

# Helper functions to generate random data
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_email():
    return f"{random_string(8).lower()}@example.com"

def random_year(start=1950, end=2023):
    return random.randint(start, end)

def random_location():
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Salem", "Dallas"]
    return random.choice(locations)

# Generate and post 100 random entries
for _ in range(1000):
    data = {
        "name": random_string(),
        "location": random_location(),
        "established_year": random_year(),
        "contact_email": random_email()
    }
    
    response = requests.post(API_URL, json=data)
    if response.status_code == 200:
        print(f"Created: {data}")
    else:
        print(f"Failed to create: {data} | Status Code: {response.status_code} | Response: {response.text}")
