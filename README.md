# Nick's Ad Enhancer

This is a Python 3 Flask app hosted on an AWS Linux box. (Contact me for the address if you need it!)

This app first checks to see if the ip address is from the US (bonus 1), and proceeds to inject
up to 5 pieces of data into the original post request before sending it back. Since the publisher_id is required,
we check that second and abandon the request if we fail to get it (bonus 2). By taking the extra steps of
integrating this with AWS, we have a substantial number of real-time metrics for the application (bonus 3).

Note: Because it takes MaxMind multiple business days to supply a free account, I used a library
built around it that doesn't require a license, and so it may be less reliable.


### Areas for improvement

1) Asynchronous HTTP requests using AIOHttp, or something similar

2) Caching/memoization of the publisher and demographics information that rarely changes

3) Better testing! These tests cover minimal cases, but more focused tests would be more effective

4) Metrics. I manually tested the latency, but it would be great to have metrics set up to check the amount of time
it takes things to run (although even free-tier AWS comes with much of that functionality built in).

### Instructions to Run:

1) `python -m venv venv`
2) `source venv/bin/activate`
3) `pip install -r requirements.txt`
4) `python tests.py`
5) `python app.py`