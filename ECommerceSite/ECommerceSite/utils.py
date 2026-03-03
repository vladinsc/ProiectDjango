from django.core.mail import mail_admins
from django.utils.html import strip_tags


def trimite_mail_admin_custom(subiect, mesaj_text, continut_html_extra=""):

    html_message = f"""
    <html>
        <body>
            <h1 style="color: red;">{subiect}</h1>
            <p>{mesaj_text}</p>
            {continut_html_extra}
        </body>
    </html>
    """
    mail_admins(
        subject=subiect,
        message=mesaj_text,
        html_message=html_message
    )