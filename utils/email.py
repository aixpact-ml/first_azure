from flask_mail import Message
from webapp.extensions import mail
# from .decorators import fire_and_forget
from jinja2 import Template
import os


# print([f for f in os.walk('./utils/')])


# @fire_and_forget
def send_async_email(msg):
    from webapp.app import app
    with app.app_context():
        mail.send(msg)


def send_email(recipients, filename):

    # Use template outside flask app
    with open('./utils/templates/email_message.html') as f:
        html_template = Template(f.read())

    try:
        msg = Message('hAPIdays from AIxPact',
                      sender='frank@aixpact.com',
                      bcc='frank@aixpact.nl',
                      recipients=[recipients])
        name = recipients.split('@')[0].lower().capitalize()
        try:
            # msg.body = template
            msg.html = html_template.render(recipients=recipients, filename=filename)
            # render_template(f'./email_message.html', recipients, filename)
        except Exception as err:
            print('msg.body err:', err)
            msg.body = f"""Hi {name},
            Thank you for joining hAPIdays, enjoy your result!
            Download: {filename}

            Cheers, Frank
            """
            # msg.html = None

        send_async_email(msg)
    except Exception as err:
        print('raised exception:', err)

# # @fire_and_forget
# def send_async_email(msg):
#     from webapp.app import app
#     with app.app_context():
#         mail.send(msg)


# def send_email(recipients, filename, template):
#     from webapp.app import app
#     try:
#         msg = Message('hAPIdays from AIxPact',
#                       sender='frank@aixpact.com',
#                       bcc='frank@aixpact.nl',
#                       recipients=[recipients])
#         name = recipients.split('@')[0].lower().capitalize()
#         try:
#             msg.body = render_template('base/email_message.txt', name=name) #, name=name, filename=filename)
#         except Exception as err:
#             print('msg.body err:', err)
#             msg.body = 'Hi ' + name + ', \n Thank you for joining hAPIdays, enjoy your result! [code]\n'
#         send_async_email(app, msg)
#     except Exception as err:
#         print('raised exception:', err)


# def send_email(template, recipients, filename):
#     try:
#         msg = Message('hAPIdays from AIxPact',
#                       sender='frank@aixpact.com',
#                       bcc='frank@aixpact.nl',
#                       recipients=[recipients])
#         name = recipients.split('@')[0].lower().capitalize()
#         print('DEBUG name', name)

#         try:
#             print(template)
#             msg.body = template  # render_template('base/email_message.txt', name=name) #, name=name, filename=filename)
#             print('DEBUG body', msg.body)
#         except Exception as err:
#             print('msg.body err:', err)
#             msg.body = 'Hi ' + name + ', \n Thank you for joining hAPIdays, enjoy your result! code\n'
#             msg.html = template
#             print('DEBUG body except', msg.body)
#         # msg.html = render_template('base/email_message.html', name=name, filename=filename)

#         # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
#         # mime = mimetypes.guess_type(filename, strict=False)[0] or 'text/plain'
#         # with open(filename, 'rb', buffering=0) as f:
#         #     # with current_app.open_resource(filename, 'rb') as f:
#         #     # TODO doesnot work from Azure - doesnot download file
#         #     msg.attach(filename, mime, f.read())

#         send_async_email(msg)


#     except Exception as err:
#         print('raised exception:', err)
