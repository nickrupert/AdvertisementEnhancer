from flask import Flask, request
import requests
import json
from geolite2 import geolite2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    data = request.get_json()

    geo = get_source_country(data['device']['ip'])
    if geo and geo != 'United States':
        return False

    # Do publisher id as early as possible, because if that's missing, we can avoid wasting time on the request
    publisher = get_publisher_info(data['site']['id'])
    publisher_id = publisher['publisher']['id']
    publisher_name = publisher['publisher']['name']

    percent_female = None
    percent_male = None

    if publisher_id:
        percent_female = get_demographics_info(data['site']['id'])
        percent_male = 100.0 - percent_female

        data = inject_data(data, publisher_id, publisher_name, percent_female, percent_male, geo)

    # Post back data
    return json.dumps(data)

def get_publisher_info(site_id):
    if site_id:
        data = {"q":{"siteID":str(site_id)}}
        r = requests.post('http://159.89.185.155:3000/api/publishers/find', json=data)
        return json.loads(r.text)
    else:
        return None

def get_demographics_info(site_id):
    d = requests.get('http://159.89.185.155:3000/api/sites/{}/demographics'.format(site_id))
    demographics_dict = json.loads(d.text)
    return demographics_dict.get('demographics', {}).get('pct_female', None)

def get_source_country(ip):
    reader = geolite2.reader()
    return reader.get(ip)['country']['names']['en']

def inject_data(data, pub_id, pub_name, female, male, geo):
    # Initialize the parts of the dict that weren't present in the input
    data['site']['publisher'] = {}
    data['site']['demographics'] = {}
    data['device']['geo'] = {}

    data['site']['publisher']['id'] = pub_id
    data['site']['publisher']['name'] = pub_name
    data['site']['demographics']['female_percent'] = female
    data['site']['demographics']['male_percent'] = male
    data['device']['geo']['country'] = geo

    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)