from influxdb_client import InfluxDBClient


class InfluxBase:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket

    def __enter__(self):
        self.influx = InfluxDBClient(url=self._url, token=self._token, org=self._org)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.influx.close()