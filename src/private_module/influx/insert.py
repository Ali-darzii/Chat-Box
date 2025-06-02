from utils.base_influx import InfluxBase
from influxdb_client import Point, WritePrecision
from datetime import datetime
import pytz

class PrivateInfluxDB(InfluxBase):

    def insert(self, box_id, sender_id,message="", file=""):
        message_insert = (Point(f"private_{box_id}")
                          .tag("sender_id", sender_id)
                          .tag("file", file)
                          .tag("message", message)
                          .time(datetime.now(pytz.timezone('Asia/Tehran')), WritePrecision.NS)
                          )
        self.influx_write_api.write(self._bucket, self._org, [message_insert])