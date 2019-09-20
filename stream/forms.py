from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.validators import InputRequired, Length, NumberRange
from wtforms.fields import StringField, SubmitField, SelectField, IntegerField, FormField, BooleanField, FloatField

import app.common.constants as constants
from app.common.stream.entry import IStream, HardwareStream, ProxyStream, RelayStream, EncodeStream, \
    TimeshiftRecorderStream, \
    CatchupStream, TimeshiftPlayerStream, TestLifeStream, VodRelayStream, VodEncodeStream, CodRelayStream, \
    CodEncodeStream, StreamLogLevel
from app.common.common_forms import InputUrlsForm, OutputUrlsForm, SizeForm, LogoForm, RationalForm, TagListField


class IStreamForm(FlaskForm):
    tvg_id = StringField(lazy_gettext(u'Tvg-ID:'),
                         validators=[
                             Length(min=constants.MIN_STREAM_TVG_ID_LENGTH, max=constants.MAX_STREAM_TVG_ID_LENGTH)])
    name = StringField(lazy_gettext(u'Name:'),
                       validators=[InputRequired(),
                                   Length(min=constants.MIN_STREAM_NAME_LENGTH, max=constants.MAX_STREAM_NAME_LENGTH)])
    tvg_name = StringField(lazy_gettext(u'Tvg-Name:'), validators=[])
    tvg_logo = StringField(lazy_gettext(u'Icon:'),
                           validators=[InputRequired(),
                                       Length(min=constants.MIN_URL_LENGTH, max=constants.MAX_URL_LENGTH)])
    group_title = StringField(lazy_gettext(u'Group:'), validators=[])
    tags = TagListField(lazy_gettext(u'Tags:'))
    price = FloatField(lazy_gettext(u'Price:'),
                       validators=[InputRequired(), NumberRange(constants.MIN_PRICE, constants.MAX_PRICE)])
    output = FormField(OutputUrlsForm, lazy_gettext(u'Output:'))
    submit = SubmitField(lazy_gettext(u'Confirm'))

    def make_entry(self) -> IStream:
        return self.update_entry(IStream())

    def update_entry(self, entry: IStream) -> IStream:
        entry.tvg_id = self.tvg_id.data
        entry.name = self.name.data
        entry.tvg_name = self.tvg_name.data
        entry.tvg_logo = self.tvg_logo.data
        entry.group_title = self.group_title.data
        entry.tags = self.tags.data
        entry.price = self.price.data
        entry.output = self.output.get_data()
        return entry


class ProxyStreamForm(IStreamForm):
    def make_entry(self):
        return self.update_entry(ProxyStream())

    def update_entry(self, entry: ProxyStream):
        return super(ProxyStreamForm, self).update_entry(entry)


class HardwareStreamForm(IStreamForm):
    AVAILABLE_LOG_LEVELS_PAIRS = [(StreamLogLevel.LOG_LEVEL_EMERG, 'EVERG'), (StreamLogLevel.LOG_LEVEL_ALERT, 'ALERT'),
                                  (StreamLogLevel.LOG_LEVEL_CRIT, 'CRITICAL'),
                                  (StreamLogLevel.LOG_LEVEL_ERR, 'ERROR'),
                                  (StreamLogLevel.LOG_LEVEL_WARNING, 'WARNING'),
                                  (StreamLogLevel.LOG_LEVEL_NOTICE, 'NOTICE'),
                                  (StreamLogLevel.LOG_LEVEL_INFO, 'INFO'),
                                  (StreamLogLevel.LOG_LEVEL_DEBUG, 'DEBUG')]

    input = FormField(InputUrlsForm, lazy_gettext(u'Input:'))
    log_level = SelectField(lazy_gettext(u'Log level:'), validators=[], choices=AVAILABLE_LOG_LEVELS_PAIRS,
                            coerce=StreamLogLevel.coerce)
    audio_select = IntegerField(lazy_gettext(u'Audio select:'),
                                validators=[InputRequired(), NumberRange(constants.INVALID_AUDIO_SELECT, 1000)])
    have_video = BooleanField(lazy_gettext(u'Have video:'), validators=[])
    have_audio = BooleanField(lazy_gettext(u'Have audio:'), validators=[])
    loop = BooleanField(lazy_gettext(u'Loop:'), validators=[])
    avformat = BooleanField(lazy_gettext(u'Avformat:'), validators=[])
    restart_attempts = IntegerField(lazy_gettext(u'Max restart attempts and frozen:'),
                                    validators=[NumberRange(1, 1000)])
    auto_exit_time = IntegerField(lazy_gettext(u'Auto exit time:'), validators=[])

    def make_entry(self):
        return self.update_entry(HardwareStream())

    def update_entry(self, entry: HardwareStream):
        entry.input = self.input.get_data()

        entry.audio_select = self.audio_select.data
        entry.have_video = self.have_video.data
        entry.have_audio = self.have_audio.data
        entry.log_level = self.log_level.data
        entry.loop = self.loop.data
        entry.avformat = self.avformat.data
        entry.restart_attempts = self.restart_attempts.data
        entry.auto_exit_time = self.auto_exit_time.data
        return super(HardwareStreamForm, self).update_entry(entry)


class RelayStreamForm(HardwareStreamForm):
    video_parser = SelectField(lazy_gettext(u'Video parser:'), validators=[],
                               choices=constants.AVAILABLE_VIDEO_PARSERS)
    audio_parser = SelectField(lazy_gettext(u'Audio parser:'), validators=[],
                               choices=constants.AVAILABLE_AUDIO_PARSERS)

    def make_entry(self):
        return self.update_entry(RelayStream())

    def update_entry(self, entry: RelayStream):
        entry.video_parser = self.video_parser.data
        entry.audio_parser = self.audio_parser.data
        return super(RelayStreamForm, self).update_entry(entry)


class EncodeStreamForm(HardwareStreamForm):
    relay_video = BooleanField(lazy_gettext(u'Relay video:'), validators=[])
    relay_audio = BooleanField(lazy_gettext(u'Relay audio:'), validators=[])
    deinterlace = BooleanField(lazy_gettext(u'Deinterlace:'), validators=[])
    frame_rate = IntegerField(lazy_gettext(u'Frame rate:'),
                              validators=[InputRequired(),
                                          NumberRange(constants.INVALID_FRAME_RATE, constants.MAX_FRAME_RATE)])
    volume = FloatField(lazy_gettext(u'Volume:'),
                        validators=[InputRequired(), NumberRange(constants.MIN_VOLUME, constants.MAX_VOLUME)])
    video_codec = SelectField(lazy_gettext(u'Video codec:'), validators=[],
                              choices=constants.AVAILABLE_VIDEO_CODECS)
    audio_codec = SelectField(lazy_gettext(u'Audio codec:'), validators=[],
                              choices=constants.AVAILABLE_AUDIO_CODECS)
    audio_channels_count = IntegerField(lazy_gettext(u'Audio channels count:'),
                                        validators=[InputRequired(), NumberRange(constants.INVALID_AUDIO_CHANNELS_COUNT,
                                                                                 constants.MAX_AUDIO_CHANNELS_COUNT)])
    size = FormField(SizeForm, lazy_gettext(u'Size:'), validators=[])
    video_bit_rate = IntegerField(lazy_gettext(u'Video bit rate:'), validators=[InputRequired()])
    audio_bit_rate = IntegerField(lazy_gettext(u'Audio bit rate:'), validators=[InputRequired()])
    logo = FormField(LogoForm, lazy_gettext(u'Logo:'), validators=[])
    aspect_ratio = FormField(RationalForm, lazy_gettext(u'Aspect ratio:'), validators=[])

    def make_entry(self):
        return self.update_entry(EncodeStream())

    def update_entry(self, entry: EncodeStream):
        entry.relay_video = self.relay_video.data
        entry.relay_audio = self.relay_audio.data
        entry.deinterlace = self.deinterlace.data
        entry.frame_rate = self.frame_rate.data
        entry.volume = self.volume.data
        entry.video_codec = self.video_codec.data
        entry.audio_codec = self.audio_codec.data
        entry.audio_channels_count = self.audio_channels_count.data
        entry.size = self.size.get_data()
        entry.video_bit_rate = self.video_bit_rate.data
        entry.audio_bit_rate = self.audio_bit_rate.data
        entry.logo = self.logo.get_data()
        entry.aspect_ratio = self.aspect_ratio.get_data()
        return super(EncodeStreamForm, self).update_entry(entry)


class TimeshiftRecorderStreamForm(RelayStreamForm):
    timeshift_chunk_duration = IntegerField(lazy_gettext(u'Chunk duration:'),
                                            validators=[InputRequired(),
                                                        NumberRange(constants.MIN_TIMESHIFT_CHUNK_DURATION,
                                                                    constants.MAX_TIMESHIFT_CHUNK_DURATION)])
    timeshift_chunk_life_time = IntegerField(lazy_gettext(u'Chunk life time:'),
                                             validators=[InputRequired(),
                                                         NumberRange(
                                                             constants.MIN_TIMESHIFT_CHUNK_LIFE_TIME,
                                                             constants.MAX_TIMESHIFT_CHUNK_LIFE_TIME)])

    def make_entry(self):
        return self.update_entry(TimeshiftRecorderStream())

    def update_entry(self, entry: TimeshiftRecorderStream):
        entry.timeshift_chunk_duration = self.timeshift_chunk_duration.data
        entry.timeshift_chunk_life_time = self.timeshift_chunk_life_time.data
        return super(TimeshiftRecorderStreamForm, self).update_entry(entry)


class CatchupStreamForm(TimeshiftRecorderStreamForm):
    def make_entry(self):
        return self.update_entry(CatchupStream())


class TimeshiftPlayerStreamForm(RelayStreamForm):
    timeshift_dir = StringField(lazy_gettext(u'Chunks directory:'), validators=[InputRequired()])
    timeshift_delay = IntegerField(lazy_gettext(u'Delay:'), validators=[InputRequired(),
                                                                        NumberRange(constants.MIN_TIMESHIFT_DELAY,
                                                                                    constants.MAX_TIMESHIFT_DELAY)])

    def make_entry(self):
        return self.update_entry(TimeshiftPlayerStream())

    def update_entry(self, entry: TimeshiftPlayerStream):
        entry.timeshift_delay = self.timeshift_delay.data
        entry.timeshift_dir = self.timeshift_dir.data
        return super(TimeshiftPlayerStreamForm, self).update_entry(entry)


class TestLifeStreamForm(RelayStreamForm):
    def make_entry(self):
        return self.update_entry(TestLifeStream())

    def update_entry(self, entry: TestLifeStream):
        return super(TestLifeStreamForm, self).update_entry(entry)


class VodRelayStreamForm(RelayStreamForm):
    def make_entry(self):
        return self.update_entry(VodRelayStream())

    def update_entry(self, entry: VodRelayStream):
        return super(VodRelayStreamForm, self).update_entry(entry)


class VodEncodeStreamForm(EncodeStreamForm):
    def make_entry(self):
        return self.update_entry(VodEncodeStream())

    def update_entry(self, entry: VodEncodeStream):
        return super(VodEncodeStreamForm, self).update_entry(entry)


class CodRelayStreamForm(RelayStreamForm):
    def make_entry(self):
        return self.update_entry(CodRelayStream())

    def update_entry(self, entry: CodRelayStream):
        return super(CodRelayStreamForm, self).update_entry(entry)


class CodEncodeStreamForm(EncodeStreamForm):
    def make_entry(self):
        return self.update_entry(CodEncodeStream())

    def update_entry(self, entry: CodEncodeStream):
        return super(CodEncodeStreamForm, self).update_entry(entry)