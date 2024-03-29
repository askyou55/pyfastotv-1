from wtforms import Form
from flask_babel import lazy_gettext
from wtforms.fields import StringField, FieldList, IntegerField, FormField, FloatField, SelectField, BooleanField, Field
from wtforms.validators import InputRequired, Length, NumberRange
from wtforms.widgets import TextInput

import app.common.constants as constants
from app.common.common_entries import Rational, Size, Logo, InputUrls, InputUrl, OutputUrls, OutputUrl, HostAndPort, \
    HttpProxy


class UrlForm(Form):
    id = IntegerField(lazy_gettext(u'Id:'),
                      validators=[InputRequired()], render_kw={'readonly': 'true'})
    uri = StringField(lazy_gettext(u'Url:'),
                      validators=[InputRequired(),
                                  Length(min=constants.MIN_URL_LENGTH, max=constants.MAX_URL_LENGTH)])


class HttpProxyForm(Form):
    url = StringField(lazy_gettext(u'Url:'), validators=[])
    user = StringField(lazy_gettext(u'User:'), validators=[])
    password = StringField(lazy_gettext(u'Password:'), validators=[])

    def get_data(self) -> HttpProxy:
        proxy = HttpProxy()
        proxy_data = self.data
        proxy.path = proxy_data['url']
        proxy.x = proxy_data['user']
        proxy.y = proxy_data['password']
        return proxy


class InputUrlForm(UrlForm):
    AVAILABLE_USER_AGENTS = [(constants.UserAgent.GSTREAMER, 'GStreamer'), (constants.UserAgent.VLC, 'VLC'),
                             (constants.UserAgent.FFMPEG, 'FFmpeg'), (constants.UserAgent.WINK, 'WINK'), ]

    user_agent = SelectField(lazy_gettext(u'User agent:'), validators=[InputRequired()], choices=AVAILABLE_USER_AGENTS,
                             coerce=constants.UserAgent.coerce)
    stream_link = BooleanField(lazy_gettext(u'SteamLink:'), validators=[])
    proxy = FormField(HttpProxyForm, lazy_gettext(u'Http proxy:'), validators=[])


class InputUrlsForm(Form):
    urls = FieldList(FormField(InputUrlForm, lazy_gettext(u'Urls:')), min_entries=1, max_entries=10)

    def get_data(self) -> InputUrls:
        urls = InputUrls()
        for url in self.data['urls']:
            input = InputUrl(url['id'], url['uri'], url['user_agent'], url['stream_link'], url['proxy'])
            urls.urls.append(input)

        return urls


class OutputUrlForm(UrlForm):
    http_root = StringField(lazy_gettext(u'Http root:'),
                            validators=[InputRequired(),
                                        Length(min=constants.MIN_PATH_LENGTH, max=constants.MAX_PATH_LENGTH)],
                            render_kw={'readonly': 'true'})


class OutputUrlsForm(Form):
    urls = FieldList(FormField(OutputUrlForm, lazy_gettext(u'Urls:')), min_entries=1, max_entries=10)

    def get_data(self) -> OutputUrls:
        urls = OutputUrls()
        for url in self.data['urls']:
            urls.urls.append(OutputUrl(url['id'], url['uri'], url['http_root']))

        return urls


class LogoForm(Form):
    path = StringField(lazy_gettext(u'Path:'), validators=[])
    x = IntegerField(lazy_gettext(u'Pos x:'), validators=[InputRequired()])
    y = IntegerField(lazy_gettext(u'Pos y:'), validators=[InputRequired()])
    alpha = FloatField(lazy_gettext(u'Alpha:'),
                       validators=[InputRequired(), NumberRange(constants.MIN_ALPHA, constants.MAX_ALPHA)])

    def get_data(self) -> Logo:
        logo = Logo()
        logo_data = self.data
        logo.path = logo_data['path']
        logo.x = logo_data['x']
        logo.y = logo_data['y']
        logo.alpha = logo_data['alpha']
        return logo


class SizeForm(Form):
    width = IntegerField(lazy_gettext(u'Width:'), validators=[InputRequired()])
    height = IntegerField(lazy_gettext(u'Height:'), validators=[InputRequired()])

    def get_data(self) -> Size:
        size = Size()
        size_data = self.data
        size.width = size_data['width']
        size.height = size_data['height']
        return size


class RationalForm(Form):
    num = IntegerField(lazy_gettext(u'Numerator:'), validators=[InputRequired()])
    den = IntegerField(lazy_gettext(u'Denominator:'), validators=[InputRequired()])

    def get_data(self) -> Rational:
        ratio = Rational()
        ratio_data = self.data
        ratio.num = ratio_data['num']
        ratio.den = ratio_data['den']
        return ratio


class HostAndPortForm(Form):
    host = StringField(lazy_gettext(u'Host:'), validators=[InputRequired()])
    port = IntegerField(lazy_gettext(u'Port:'), validators=[InputRequired()])

    def get_data(self) -> HostAndPort:
        host = HostAndPort()
        host_data = self.data
        host.host = host_data['host']
        host.port = host_data['port']
        return host


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        """values on load"""
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []
