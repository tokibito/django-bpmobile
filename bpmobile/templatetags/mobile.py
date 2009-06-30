# -*- coding: utf-8 -*-
"""
django用のテンプレートタグ
uamobile必須です
"""
import os
import urlparse
import cgi
from django import template
from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.template.defaulttags import URLNode
from bpmobile import utils as utils

register = template.Library()

def _image_tag_emoji(src, alt):
    return '<img src="%s" width="16" height="16" alt="%s" />' % (src, alt)

class EmojiNode(template.Node):
    def __init__(self, code):
        self.code = code.upper()

    def __repr__(self):
        return "<EmojiNode>"

    def _get_image_tag(self):
        return _image_tag_emoji(urlparse.urljoin(settings.MEDIA_URL or u'/', 'img/emoticons/%s'), utils.name2ja(self.code))
    image_tag = property(_get_image_tag)

    def render(self, context):
        agent = context.get('agent', None)
        output = utils.convert_emoji(utils.uni_name2docomo(self.code), agent, image_tag_callback=lambda src, alt: self.image_tag % src)
        return output

@register.tag
def emoji(parser, token):
    """
    絵文字タグ
    {% emoji "名前" %}
    """
    args = token.split_contents()

    if len(args) == 2:
        if not (args[1][0] == args[1][-1] and args[1][0] in ('"', "'")):
            raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % args[0])
        return EmojiNode(args[1][1:-1])
    else:
        raise template.TemplateSyntaxError("'emoji' tag require one arguments")

class EmojiContentsNode(template.Node):
    def __init__(self, nodelist, removevar=None):
        self.removevar = removevar
        self.nodelist = nodelist

    def __repr__(self):
        return "<EmojiContentsNode>"

    def _get_image_tag(self):
        return _image_tag_emoji(urlparse.urljoin(settings.MEDIA_URL or u'/', 'img/emoticons/%s'), '%s')
    image_tag = property(_get_image_tag)

    def render(self, context):
        agent = context.get('agent', None)
        output = self.nodelist.render(context)
        output = utils.convert_emoji(output, agent, self.removevar, lambda src, alt: self.image_tag % (src, alt))
        return output

@register.tag
def emojicontents(parser, token):
    """
    絵文字
    {% emojicontents %}{% endemojicontents %}
    """
    nodelist = parser.parse(('endemojicontents',))
    parser.delete_first_token()
    args = token.split_contents()
    if len(args) == 2:
        return EmojiContentsNode(nodelist, args[1])
    return EmojiContentsNode(nodelist)

class MobileURLNode(URLNode):
    def __init__(self, view_name, args, kwargs, asvar, params, anchor, guid):
        super(MobileURLNode, self).__init__(view_name, args, kwargs, asvar)
        self.params = params
        self.guid = guid
        self.anchor = anchor

    def render(self, context):
        url = super(MobileURLNode, self).render(context)
        p, d, path, params, anc = urlparse.urlsplit(url)
        agent = context.get('agent', None)
        params_list = params and cgi.parse_qs(params) or {}
        anc = self.anchor or anc
        for k, v in self.params.iteritems():
            val = v.resolve(context)
            if val is None:
                val = ''
            val = force_unicode(val, errors='replace')
            if agent.is_softbank():
                params_list[k] = val.encode('utf-8')
            else:
                params_list[k] = val.encode('cp932')
        if agent:
            if agent.is_docomo():
                # DoCoMoの場合はguid=onをつける
                if not params_list.has_key('guid') and self.guid:
                    params_list['guid'] = 'on'
        url = urlparse.urlunsplit((p, d, path, urllib.urlencode(params_list), anc))
        if self.asvar:
            context[self.asvar] = url
            return ''
        return url

@register.tag
def mobileurl(parser, token):
    """
    モバイル用urlタグ
    docomoの場合は guid=on を付加
    _params=... にGETパラメータを記述
    _noguid を入れるとguid=onの付加をスキップ
    """
    bits = token.contents.split(' ')
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    params = {}
    anchor = None
    guid = True
        
    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if arg == '_noguid':
                        guid = False
                        continue
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        # params
                        if k == '_params':
                            for p in v.split('&'):
                                kp, vp = p.split('=')
                                kp = kp.strip()
                                params[kp] = parser.compile_filter(vp)
                        elif k == '_anchor':
                            anchor = v.strip()
                        else:
                            kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return MobileURLNode(viewname, args, kwargs, asvar, params, anchor, guid)

# モバイル入力モード
MODE_HIRAGANA = 'hiragana'
MODE_HANKANA = 'hankana'
MODE_ALPHABET = 'alphabet'
MODE_NUMERIC = 'numeric'

MOBILE_INPUT_FORMAT_DOCOMO = {
    MODE_HIRAGANA: {'style': mark_safe("-wap-input-format:'*<ja:h>'")},
    MODE_HANKANA: {'style': mark_safe("-wap-input-format:'*<ja:hk>'")},
    MODE_ALPHABET: {'style': mark_safe("-wap-input-format:'*<ja:en>'")},
    MODE_NUMERIC: {'style': mark_safe("-wap-input-format:'*<ja:n>'")},
}
MOBILE_INPUT_FORMAT_EZWEB = {
    MODE_HIRAGANA: {'istyle': '1', 'format': '*M'},
    MODE_HANKANA: {'istyle': '2', 'format': '*m'},
    MODE_ALPHABET: {'istyle': '3', 'format': '*m'},
    MODE_NUMERIC: {'istyle': '4', 'format': '*N'},
}
MOBILE_INPUT_FORMAT_SOFTBANK = {
    MODE_HIRAGANA: {'istyle': '1', 'mode': 'hiragana'},
    MODE_HANKANA: {'istyle': '2', 'format': 'hankakukana'},
    MODE_ALPHABET: {'istyle': '3', 'format': 'alphabet'},
    MODE_NUMERIC: {'istyle': '4', 'format': 'numeric'},
}
class MobileInputFormatNode(template.Node):
    def __init__(self, field, mode):
        self.field = template.Variable(field)
        self.mode = mode

    def __repr__(self):
        return "<MobileInputFormatNode>"

    def render(self, context):
        bd_field = self.field.resolve(context)
        agent = context.get('agent', None)
        # widgetを切り替える
        if agent and agent.is_docomo():
            widget = forms.widgets.TextInput(attrs=MOBILE_INPUT_FORMAT_DOCOMO[self.mode])
        elif agent and agent.is_ezweb():
            widget = forms.widgets.TextInput(attrs=MOBILE_INPUT_FORMAT_EZWEB[self.mode])
        elif agent and agent.is_softbank():
            widget = forms.widgets.TextInput(attrs=MOBILE_INPUT_FORMAT_SOFTBANK[self.mode])
        else:
            widget = bd_field.field.widget
        return bd_field.as_widget(widget=widget)

@register.tag
def mobile_input_format(parser, token):
    """
    モバイル向け入力モードを指定テキストフィールド
    {% mobile_input_format myform.myfield alphabet %}
    """
    args = token.split_contents()
    if len(args) == 3:
        return MobileInputFormatNode(args[1], args[2])
    raise template.TemplateSyntaxError("'mobile_input_format' tag require two arguments")

class MobileEncodingNode(template.Node):
    def __repr__(self):
        return "<MobileEncodingNode>"

    def render(self, context):
        agent = context.get('agent', None)
        encoding = 'UTF-8'
        if agent and agent.is_docomo():
            encoding = 'Shift_JIS'
        elif agent and agent.is_ezweb():
            encoding = 'Shift_JIS'
        return encoding

@register.tag
def mobile_encoding(parser, token):
    """
    キャリアに応じた文字コード
    {% mobile_encoding %}
    """
    args = token.split_contents()

    if len(args) > 1:
        raise template.TemplateSyntaxError("'mobile_encoding' tag are no arguments")
    else:
        return MobileEncodingNode()
