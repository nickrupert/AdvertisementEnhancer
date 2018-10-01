from flask import Flask, request
from geolite2 import geolite2
import json
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_request():
    """
    Handle a request and call the various micro-services to update the incoming request
    """
    data = request.get_json()

    # Check the country of origin and return an error message if the IP isn't from the US
    geo = get_source_country(data['device']['ip'])
    if geo and geo != 'United States':
        error = {'error': 'This service is not available for non-US IP addresses at this time'}
        return json.dumps(error)

    # Do publisher id as early as possible, because if that's missing, we can avoid wasting time on the request
    publisher = get_publisher_info(data['site']['id'])
    publisher_id = publisher['publisher']['id']
    publisher_name = publisher['publisher']['name']

    percent_female = None
    percent_male = None

    if publisher_id:
        percent_female = get_demographics_info(data['site']['id'])
        if percent_female:
            percent_male = 100.0 - percent_female

        data = inject_data(data, publisher_id, publisher_name, percent_female, percent_male, geo)
    else:
        # If there's no publisher ID, fail and return False
        return False

    # Post back the request after it was injected with additional data
    return json.dumps(data)


def get_publisher_info(site_id):
    """Finds the publisher name and id from the publisher service

        Arguments:
            site_id -- the id of the site making the request
        """
    if site_id:
        data = {"q":{"siteID":str(site_id)}}
        r = requests.post('http://159.89.185.155:3000/api/publishers/find', json=data)
        return json.loads(r.text)
    else:
        return None


def get_demographics_info(site_id):
    """ Finds the percent of females visiting a given site

    Arguments:
        site_id -- the id of the site making the request
    """
    d = requests.get('http://159.89.185.155:3000/api/sites/{}/demographics'.format(site_id))
    demographics_dict = json.loads(d.text)
    return demographics_dict.get('demographics', {}).get('pct_female', None)


def get_source_country(ip):
    """ Finds the country of origin for the IP address of the incoming request where the site was served

    Arguments:
        ip -- IP address of the the user who visited the site
    """
    reader = geolite2.reader()
    return reader.get(ip)['country']['names']['en']


def inject_data(data, pub_id, pub_name, female, male, geo):
    """ Updates the data of the input with the info found from the various micro-services

    Arguments:
        data -- The input data
        pub_id -- The publisher's ID
        pub_name -- The publisher's name
        female -- The percent of visitors to the site who are female
        male -- The percent of visitors to the site who are female
        geo -- The country of origin
    """
    # Initialize the parts of the dict that weren't present in the input
    data['site']['publisher'] = {}
    data['site']['demographics'] = {}
    data['device']['geo'] = {}

    if pub_id:
        data['site']['publisher']['id'] = pub_id
    if pub_name:
        data['site']['publisher']['name'] = pub_name
    if female:
        data['site']['demographics']['female_percent'] = female
    if male:
        data['site']['demographics']['male_percent'] = male
    if geo:
        data['device']['geo']['country'] = geo

    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)