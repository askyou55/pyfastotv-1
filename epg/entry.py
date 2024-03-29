from mongoengine import Document, StringField

import app.common.constants as constants


class Epg(Document):
    ID_FIELD = "id"
    URI_FIELD = "uri"

    meta = {'allow_inheritance': True, 'collection': 'epg', 'auto_create_index': False}
    uri = StringField(default='http://0.0.0.0/epg.xml', max_length=constants.MAX_URL_LENGTH, required=True)
