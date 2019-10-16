from datetime import datetime
from hashlib import md5
from bson.objectid import ObjectId
from enum import IntEnum

from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, ListField, ReferenceField, \
    PULL, ObjectIdField, EmbeddedDocumentField

from app.common.subscriber.settings import Settings
from app.common.service.entry import ServiceSettings
from app.common.stream.entry import IStream, make_channel_info, make_vod_info
from app.common.stream.stream_data import BaseInfo
import app.common.constants as constants


class Device(EmbeddedDocument):
    ID_FIELD = 'id'
    NAME_FIELD = 'name'
    STATUS_FIELD = 'status'
    CREATED_DATE_FIELD = 'created_date'

    DEFAULT_DEVICE_NAME = 'Device'
    MIN_DEVICE_NAME_LENGTH = 3
    MAX_DEVICE_NAME_LENGTH = 32

    class Status(IntEnum):
        NOT_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

        @classmethod
        def choices(cls):
            return [(choice, choice.name) for choice in cls]

        @classmethod
        def coerce(cls, item):
            return cls(int(item)) if not isinstance(item, cls) else item

        def __str__(self):
            return str(self.value)

    meta = {'allow_inheritance': False, 'auto_create_index': True}
    id = ObjectIdField(required=True, default=ObjectId, unique=True, primary_key=True)
    created_date = DateTimeField(default=datetime.now)
    status = IntField(default=Status.NOT_ACTIVE)
    name = StringField(default=DEFAULT_DEVICE_NAME, min_length=MIN_DEVICE_NAME_LENGTH,
                       max_length=MAX_DEVICE_NAME_LENGTH, required=True)

    def get_id(self):
        return str(self.id)

    def to_dict(self) -> dict:
        return {Device.ID_FIELD: self.get_id(), Device.NAME_FIELD: self.name, Device.STATUS_FIELD: self.status,
                Device.CREATED_DATE_FIELD: int(self.created_date.timestamp() * 1000)}


class Subscriber(Document):
    MAX_DATE = datetime(2100, 1, 1)
    ID_FIELD = "id"
    EMAIL_FIELD = "login"
    PASSWORD_FIELD = "password"

    class Status(IntEnum):
        NOT_ACTIVE = 0
        ACTIVE = 1
        TRIAL_FINISHED = 2
        BANNED = 3

        @classmethod
        def choices(cls):
            return [(choice, choice.name) for choice in cls]

        @classmethod
        def coerce(cls, item):
            return cls(int(item)) if not isinstance(item, cls) else item

        def __str__(self):
            return str(self.value)

    SUBSCRIBER_HASH_LENGTH = 32

    meta = {'allow_inheritance': True, 'collection': 'subscribers', 'auto_create_index': False}

    email = StringField(max_length=64, required=True)
    password = StringField(min_length=SUBSCRIBER_HASH_LENGTH, max_length=SUBSCRIBER_HASH_LENGTH, required=True)
    created_date = DateTimeField(default=datetime.now)
    exp_date = DateTimeField(default=MAX_DATE)
    status = IntField(default=Status.NOT_ACTIVE)
    country = StringField(min_length=2, max_length=3, required=True)
    language = StringField(default=constants.DEFAULT_LOCALE, required=True)

    servers = ListField(ReferenceField(ServiceSettings, reverse_delete_rule=PULL), default=[])
    devices = ListField(EmbeddedDocumentField(Device), default=[])
    streams = ListField(ReferenceField(IStream, reverse_delete_rule=PULL), default=[])
    own_streams = ListField(ReferenceField(IStream, reverse_delete_rule=PULL), default=[])
    settings = EmbeddedDocumentField(Settings, default=Settings)

    def add_server(self, server):
        self.servers.append(server)
        self.save()

    def add_device(self, device: Device):
        self.devices.append(device)
        self.save()

    def remove_device(self, sid: str):
        for device in self.devices:
            if str(device.id) == sid:
                self.devices.remove(device)
                break
        self.save()

    def find_device(self, sid: str):
        for device in self.devices:
            if str(device.id) == sid:
                return device
        return None

    def add_official_stream(self, stream: IStream):
        self.streams.append(stream)
        self.save()

    def get_official_streams(self) -> (list, list):
        streams = []
        vods = []
        for serv in self.servers:
            for stream in self.streams:
                founded_stream = serv.find_stream_settings_by_id(stream.id)
                if founded_stream:
                    stream_type = founded_stream.get_type()
                    if stream_type == constants.StreamType.VOD_RELAY or stream_type == constants.StreamType.VOD_ENCODE or stream_type == constants.StreamType.VOD_PROXY:
                        vod = make_vod_info(founded_stream, BaseInfo.Type.PUBLIC)
                        vods.append(vod.to_dict())
                    else:
                        channel = make_channel_info(founded_stream, BaseInfo.Type.PUBLIC)
                        streams.append(channel.to_dict())

        return streams, vods

    def add_own_stream(self, stream: IStream):
        self.own_streams.append(stream)
        self.save()

    def get_own_streams(self) -> (list, list):
        own_streams = []
        own_vods = []
        for founded_stream in self.own_streams:
            stream_type = founded_stream.get_type()
            if stream_type == constants.StreamType.VOD_RELAY or stream_type == constants.StreamType.VOD_ENCODE or stream_type == constants.StreamType.VOD_PROXY:
                vod = make_vod_info(founded_stream, BaseInfo.Type.PRIVATE)
                own_vods.append(vod.to_dict())
            else:
                channel = make_channel_info(founded_stream, BaseInfo.Type.PRIVATE)
                own_streams.append(channel.to_dict())
        return own_streams, own_vods

    def get_streams(self) -> (list, list):
        streams, vods = self.get_official_streams()
        own_streams, own_vods = self.get_own_streams()

        streams.extend(own_streams)
        vods.extend(own_vods)
        return streams, vods

    def get_not_active_devices(self):
        devices = []
        for dev in self.devices:
            if dev.status == Device.Status.NOT_ACTIVE:
                devices.append(dev.to_dict())

        return devices

    @staticmethod
    def make_md5_hash_from_password(password: str) -> str:
        m = md5()
        m.update(password.encode())
        return m.hexdigest()

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return Subscriber.make_md5_hash_from_password(password)

    @staticmethod
    def check_password_hash(hash: str, password: str) -> bool:
        return hash == Subscriber.generate_password_hash(password)


Subscriber.register_delete_rule(ServiceSettings, "subscribers", PULL)
