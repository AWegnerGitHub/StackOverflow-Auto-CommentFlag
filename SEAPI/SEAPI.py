import gzip
import time
import requests
from itertools import chain
import pprint

try:
    import json
except ImportError:
    import simplejson as json

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class SEAPIError(Exception):
    """Raised if an API Error is encountered."""

    def __init__(self, url, code, message):
        self.url = url
        self.code = code
        self.message = message


class SEAPI(object):
    """Provide a way to get data from SE Site."""

    def __init__(self, name=None, version="2.2", **kwargs):
        """	`name` will be used to look up base URL of site we are querying.
			`version` is the API version we are querying		
		"""
        if not name:
            raise ValueError('No Site Name provided')

        self.proxy = None
        self.max_pages = 100
        self._endpoint = None
        self._api_key = None
        self._name = None
        self._version = version
        if 'proxy' in kwargs:
            self.proxy = kwargs['proxy']
        if 'max_pages' in kwargs:
            self.max_pages = kwargs['max_pages']
        if 'key' in kwargs:
            self.key = kwargs['key']
        if 'access_token' in kwargs:
            self.access_token = kwargs['access_token']

        self._base_url = 'https://api.stackexchange.com/%s/' % (version)
        sites = self.fetch('sites', filter='!*L1*AY-85YllAr2)')
        for s in sites['items']:
            if name == s['api_site_parameter']:
                self._name = s['name']
                self._api_key = s['api_site_parameter']
                self._version = version

        if not self._name:
            raise ValueError('Invalid Site Name provided')


    def __repr__(self):
        return "<%s> v:<%s> endpoint: %s" % (self._name, self._version, self._endpoint)

    def fetch(self, endpoint=None, pagesize=100, page=1, key=None, filter='default', **kwargs):
        """Build the API end point.
		
			If `kwargs` exist, we need to tack those on too
		"""
        if not endpoint:
            raise ValueError('No end point provided.')

        self._endpoint = endpoint

        params = {
            "pagesize": pagesize,
            "page": page,
            "filter": filter
        }

        if self.key:
            params['key'] = self.key
        if self.access_token:
            params['access_token'] = self.access_token

        if 'ids' in kwargs:
            ids = ';'.join(str(x) for x in kwargs['ids'])
            kwargs.pop('ids', None)
        else:
            ids = None

        params.update(kwargs)
        if self._api_key:
            params['site'] = self._api_key

        data = []
        run_cnt = 0
        while True:
            run_cnt += 1
            if run_cnt > self.max_pages:  # Prevents Infinate Loops
                break

            base_url = "%s%s/" % (self._base_url, endpoint)
            if ids:
                base_url += "%s" % (ids)

            response = requests.get(base_url, params=params, proxies=self.proxy)
            response = response.json()
            count = 0

            try:
                error = response["error"]
                code = error["Code"]
                message = error["Message"]
                raise SEAPIError(url, code, message)
            except KeyError:
                pass  # This means there is no error

            if key:
                data.append(response[key])
            else:
                data.append(response)

            if len(data) < 1:
                break

            backoff = 0
            if 'has_more' in response and response['has_more'] == 'True':
                params["page"] += 1
                if 'backoff' in response:
                    backoff = response['backoff']
                    print "Backoff %s" % (backoff)
            else:
                break

        r = []
        for d in data:
            r.extend(d['items'])
        result = {
            'backoff': backoff,
            'has_most': data[-1]['has_more'],
            'page': params['page'],
            'quota_max': data[-1]['quota_max'],
            'quota_remaining': data[-1]['quota_remaining'],
            'items': None,
        }

        result['items'] = list(chain(r))
        return result

