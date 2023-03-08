import requests


# Is the site real?
def lookup(url):
    try:
        url = url
        response = requests.get(url)
        if response.status_code == 200:
            return url
        else:
            return None
    except requests.exceptions.RequestException:
        return None
