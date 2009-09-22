# -*- coding: utf-8 -*-

import re
from datetime import datetime,date,timedelta
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate, parseaddr, formataddr
from django.core import mail
from django.utils.encoding import smart_str
from django import template
from django.template.loader import render_to_string
from django.conf import settings

EMAIL_CHARSET = getattr(settings, "EMAIL_CHARSET", settings.DEFAULT_CHARSET)
 
def format_header(name, val):
    if '\n' in val or '\r' in val:
        raise mail.BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (val, name)) 
    if name.lower() in ('to', 'from', 'cc'):
        result = []
        for item in val.split(', '):
            nm, addr = parseaddr(item)
            nm = str(Header(
                val.encode(EMAIL_CHARSET,'replace'),
                EMAIL_CHARSET,
            ))
            result.append(formataddr((nm, str(addr))))
        val = ', '.join(result)
    elif name.lower() == 'subject':
        val = Header(
            val.encode(EMAIL_CHARSET,'replace'),
            EMAIL_CHARSET,
        )
    else:
        val = Header(val, EMAIL_CHARSET)
    
    return name,val

class JPMIMEText(MIMEText):
    def __setitem__(self, name, val):
        name,val = format_header(name,val)
        MIMEText.__setitem__(self, name, val)

class JPMIMEMultipart(MIMEMultipart):
    def __setitem__(self, name, val):
        name,val = format_header(name,val)
        MIMEText.__setitem__(self, name, val)

class JPEmailMessage(mail.EmailMessage):
    def message(self):
        encoding = self.encoding or EMAIL_CHARSET
        msg = JPMIMEText(smart_str(self.body, encoding),
                           self.content_subtype, encoding)
        if self.attachments:
            body_msg = msg
            msg = JPMIMEMultipart(_subtype=self.multipart_subtype)
            if self.body:
                msg.attach(body_msg)
            for attachment in self.attachments:
                if isinstance(attachment, MIMEBase):
                    msg.attach(attachment)
                else:
                    msg.attach(self._create_attachment(*attachment))
        msg['Subject'] = self.subject 
        msg['From'] = self.extra_headers.pop('From', self.from_email)
        msg['To'] = ', '.join(self.to)

        # Email header names are case-insensitive (RFC 2045), so we have to
        # accommodate that when doing comparisons.
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = mail.make_msgid()
        for name, value in self.extra_headers.items():
            msg[name] = value
        return msg

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None):
    """
    Djangoのsend_mailに交換できる関数。
    メールエンコーディングはsettings.pyのEMAIL_CHARSETで設定する。
    """
    connection = mail.SMTPConnection(username=auth_user, password=auth_password,
                                fail_silently=fail_silently)
    return JPEmailMessage(subject, message, from_email, recipient_list,
                          connection=connection).send()

def send_mass_mail(datatuple, fail_silently=False, auth_user=None,
                   auth_password=None):
    connection = mail.SMTPConnection(username=auth_user, password=auth_password,
                                fail_silently=fail_silently)
    messages = [JPEmailMessage(subject, message, sender, recipient)
                for subject, message, sender, recipient in datatuple]
    return connection.send_messages(messages)

def mail_admins(subject, message, fail_silently=False):
    """
    Sends a message to the admins, as defined by the ADMINS setting.
    """
    if not settings.ADMINS:
        return
    JPEmailMessage(settings.EMAIL_SUBJECT_PREFIX + subject, message,
                 settings.SERVER_EMAIL, [a[1] for a in settings.ADMINS]
                 ).send(fail_silently=fail_silently)

def mail_managers(subject, message, fail_silently=False):
    """
    Sends a message to the managers, as defined by the MANAGERS setting.
    """
    if not settings.MANAGERS:
        return
    JPEmailMessage(settings.EMAIL_SUBJECT_PREFIX + subject, message,
                   settings.SERVER_EMAIL, [a[1] for a in settings.MANAGERS]
                   ).send(fail_silently=fail_silently)
