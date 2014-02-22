import requests


class Gw2Exception(Exception):
    pass


class Gw2NotFound(Gw2Exception):
    pass


class JsonApi(object):
    _url = ""
    version = 1

    def _get(self, url, params={}):
        req = requests.get(url, params=params)
        if 200 <= req.status_code < 300:
            return req.json()
        return False

    def url(self, *args, **kwargs):
        kwargs.setdefault('version', self.version)
        return self._url.format % (version, endpoint)


class Gw2Api(object):
    _url = "https://api.guildwars2.com/v%s/%s.json"
    version = 1

    def _get(self, url, params={}):
        req = requests.get(url, params=params)
        if 200 <= req.status_code < 300:
            return req.json()
        return False

    def url(self, endpoint, version=version):
        return self._url % (version, endpoint)

    def get_items(self):
        data = self._get(self.url('items'))
        if data:
            return data.get('items', [])
        return []

    def get_item(self, id):
        data = self._get(self.url('item_details'), params={'item_id': id})
        return data

    def get_recipes(self):
        data = self._get(self.url('recipes'))
        if data:
            return data.get('recipes', [])
        return []

    def get_recipe(self, id):
        data = self._get(self.url('recipe_details'), params={'recipe_id': id})
        return data

    def describe_item(self, id):
        data = self._get(self.url('item_details'), params={'item_id': id})
        if data:
            print data
            for key in data:
                if not isinstance(data[key], unicode):
                    data[key] = json.dumps(data[key])
            print
            print data

api = Gw2Api()
