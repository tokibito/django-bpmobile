# vim:fileencoding=utf8
import os
import re
import xml.dom.minidom
import e4u.emoji4unicode as e4u_google

e4u_google.Load()

# cp932のマッピングテーブル
emoji_softbank_to_docomo = {}
emoji_kddi_to_docomo = {}
emoji_name_to_docomo = {}
emoji_docomo_to_softbank = {}
emoji_docomo_to_kddi = {}
emoji_docomo_to_name = {}
emoji_docomo = []
emoji_kddi = []
emoji_softbank = []

# unicodeのマッピング
uni_emoji_softbank_to_docomo = {}
uni_emoji_kddi_to_docomo = {}
uni_emoji_name_to_docomo = {}
uni_emoji_docomo_to_softbank = {}
uni_emoji_docomo_to_kddi = {}
uni_emoji_docomo_to_name = {}
uni_emoji_docomo = []
uni_emoji_kddi = []
uni_emoji_softbank = []

# cp932/unicode変換マッピング
kddi_cp932_to_uni = {}
kddi_uni_to_cp932 = {}
kddi_uni_to_xuni = {} # sjisと対応付けたunicodeマップ
kddi_xuni_to_uni = {} # sjisと対応付けたunicodeマップ

# nameと日本語名のマッピング
name_to_ja = {}

# nameと画像のマッピング
_images_doc = xml.dom.minidom.parse(os.path.join(os.path.dirname(__file__), 'data/emoji2image.xml'))
name_to_image_src = {}

E4U_CALLIERS = ['docomo', 'kddi', 'softbank']

def code_to_sjis(code, carrier):
    """
    16進数コード(unicode)からsjis文字列を生成
    """
    clean_code = code.replace('>', '')
    if clean_code:
        codes = ''
        for code_char in clean_code.split('+'):
            symbol = e4u_google.all_carrier_data[carrier].SymbolFromUnicode(code_char)
            codes += ''.join([chr(int(hex_char, 16)) for hex_char in re.findall('..', symbol.shift_jis)])
        return codes
    return ''

def code_to_unicode(code):
    """
    16進数コードからunicode文字列を生成
    """
    clean_code = code.replace('>', '')
    if clean_code:
        return u''.join([unichr(int(code_char, 16)) for code_char in clean_code.split('+')])
    return u''

for e in e4u_google._doc.getElementsByTagName('e'):
    docomo_code, kddi_code, softbank_code = [e.getAttribute(attr_name) for attr_name in E4U_CALLIERS]

    docomo = code_to_sjis(docomo_code, 'docomo')
    kddi = code_to_sjis(kddi_code, 'kddi')
    softbank = code_to_sjis(softbank_code, 'softbank')
    emoji_softbank_to_docomo[softbank] = docomo
    emoji_docomo_to_softbank[docomo] = softbank
    emoji_kddi_to_docomo[kddi] = docomo
    if not docomo_code.startswith('>'):
        emoji_docomo_to_kddi[docomo] = kddi
    emoji_name_to_docomo[e.getAttribute('name')] = docomo
    if docomo and not emoji_docomo_to_name.has_key(docomo):
        emoji_docomo_to_name[docomo] = e.getAttribute('name')
    if docomo:
        emoji_docomo.append(docomo)
    if kddi:
        emoji_kddi.append(kddi)
    if softbank:
        emoji_softbank.append(softbank)

    docomo_uni = code_to_unicode(docomo_code)
    kddi_uni = code_to_unicode(kddi_code)
    softbank_uni = code_to_unicode(softbank_code)
    name = e.getAttribute('name')
    uni_emoji_softbank_to_docomo[softbank_uni] = docomo_uni
    uni_emoji_kddi_to_docomo[kddi_uni] = docomo_uni
    if not docomo_code.startswith('>'):
        uni_emoji_docomo_to_kddi[docomo_uni] = kddi_uni
        uni_emoji_docomo_to_softbank[docomo_uni] = softbank_uni
        if docomo_code:
            name_ja = e4u_google.all_carrier_data['docomo'].SymbolFromUnicode(docomo_code).GetJapaneseName()
            if name_ja:
                name_to_ja[name] = name_ja
            if docomo_uni:
                uni_emoji_docomo_to_name[docomo_uni] = name
    uni_emoji_name_to_docomo[name] = docomo_uni
    if docomo_uni:
        uni_emoji_docomo.append(docomo_uni)
    if kddi_uni:
        uni_emoji_kddi.append(kddi_uni)
    if softbank_uni:
        uni_emoji_softbank.append(softbank_uni)

    if kddi and kddi_uni:
        kddi_cp932_to_uni[kddi] = kddi_uni
        kddi_uni_to_cp932[kddi_uni] = kddi
        kddi_xuni = unicode(kddi, 'cp932')
        kddi_uni_to_xuni[kddi_uni] = kddi_xuni
        kddi_xuni_to_uni[kddi_xuni] = kddi_uni

for img in _images_doc.getElementsByTagName('img'):
    name = img.getAttribute('name')
    src = img.getAttribute('src')
    if name and src:
        name_to_image_src[name] = src

RE_EMOJI_DOCOMO = re.compile('|'.join(re.escape(e) for e in emoji_docomo))
RE_EMOJI_KDDI = re.compile('|'.join(re.escape(e) for e in emoji_kddi))
RE_EMOJI_SOFTBANK = re.compile('|'.join(re.escape(e) for e in emoji_softbank))

RE_UNI_EMOJI_DOCOMO = re.compile(u'[%s]' % u''.join(re.escape(e) for e in uni_emoji_docomo))
RE_UNI_EMOJI_KDDI = re.compile(u'[%s]' % u''.join(re.escape(e) for e in uni_emoji_kddi))
RE_XUNI_EMOJI_KDDI = re.compile(u'[%s]' % u''.join(re.escape(e) for e in kddi_xuni_to_uni.keys()))
RE_UNI_EMOJI_SOFTBANK = re.compile(u'[%s]' % u''.join(re.escape(e) for e in uni_emoji_softbank))

def is_unicode(s):
    return isinstance(s, unicode) or hasattr(s, '__unicode__')

def emoji2docomo(s, is_kddi=True, is_softbank=True):
    """
    sjisの絵文字をdocomo絵文字に変換します。
    docomo絵文字にこの関数は使用しない or is_softbank=Falseで使用してください。
    kddi絵文字にこの関数を使用するときはis_softbank=Falseにしてください。
    softbankはdocomoとkddiのsjis絵文字領域とかぶっているので注意。
    """
    if is_kddi:
        s = RE_EMOJI_KDDI.sub(lambda m:emoji_kddi_to_docomo[m.group()], s)
    if is_softbank:
        s = RE_EMOJI_SOFTBANK.sub(lambda m:emoji_softbank_to_docomo[m.group()], s)
    return s

def uni_emoji2docomo(s):
    """
    unicode入力を前提としています。
    """
    s = RE_UNI_EMOJI_KDDI.sub(lambda m:uni_emoji_kddi_to_docomo[m.group()], s)
    s = RE_UNI_EMOJI_SOFTBANK.sub(lambda m:uni_emoji_softbank_to_docomo[m.group()], s)
    return s

def docomo2softbank(s):
    if is_unicode(s):
        return uni_docomo2softbank(s)
    return emoji_docomo_to_softbank.has_key(s) and emoji_docomo_to_softbank[s] or ''

def uni_docomo2softbank(s):
    return uni_emoji_docomo_to_softbank.has_key(s) and uni_emoji_docomo_to_softbank[s] or u''

def docomo2kddi(s):
    if is_unicode(s):
        return uni_docomo2kddi(s)
    return emoji_docomo_to_kddi.has_key(s) and emoji_docomo_to_kddi[s] or ''

def uni_docomo2kddi(s):
    return uni_emoji_docomo_to_kddi.has_key(s) and uni_emoji_docomo_to_kddi[s] or u''

def kddi2docomo(s):
    return emoji_kddi_to_docomo.has_key(s) and emoji_kddi_to_docomo[s] or ''

def uni_kddi2docomo(s):
    return uni_emoji_kddi_to_docomo.has_key(s) and uni_emoji_kddi_to_docomo[s] or u''

def kddi_uni2xuni(s):
    return kddi_uni_to_xuni.has_key(s) and kddi_uni_to_xuni[s] or u''

def kddi_xuni2uni(s):
    return kddi_xuni_to_uni.has_key(s) and kddi_xuni_to_uni[s] or u''

def softbank2docomo(s):
    return emoji_softbank_to_docomo.has_key(s) and emoji_softbank_to_docomo[s] or ''

def uni_softbank2docomo(s):
    return uni_emoji_softbank_to_docomo.has_key(s) and uni_emoji_softbank_to_docomo[s] or u''

def name2docomo(s):
    return emoji_name_to_docomo.has_key(s) and emoji_name_to_docomo[s] or ''

def uni_name2docomo(s):
    return uni_emoji_name_to_docomo.has_key(s) and uni_emoji_name_to_docomo[s] or u''

def docomo2name(s):
    if is_unicode(s):
        return uni_docomo2name(s)
    return emoji_docomo_to_name.has_key(s) and emoji_docomo_to_name[s] or ''

def uni_docomo2name(s):
    return uni_emoji_docomo_to_name.has_key(s) and uni_emoji_docomo_to_name[s] or u''

def name2image(s):
    return name_to_image_src.has_key(s) and name_to_image_src[s] or ''

def name2ja(s):
    return name_to_ja.has_key(s) and name_to_ja[s] or u''

def _image_tag_emoji(src, alt):
    return '<img src="/img/emoticons/%s" width="16" height="16" alt="%s" />' % (src, alt)

def convert_emoji(s, agent=None, remove=False, image_tag_callback=None):
    if agent:
        if agent.is_nonmobile():
            # PCの場合
            if remove:
                s = RE_UNI_EMOJI_DOCOMO.sub(u'', s)
            else:
                if not callable(image_tag_callback):
                    image_tag_callback = _image_tag_emoji
                s = RE_UNI_EMOJI_DOCOMO.sub(lambda m: image_tag_callback(name2image(uni_docomo2name(m.group())), name2ja(m.group())), s)
        elif agent.is_softbank():
            #softbank
            s = RE_UNI_EMOJI_DOCOMO.sub(lambda m: uni_docomo2softbank(m.group()), s)
    return s

