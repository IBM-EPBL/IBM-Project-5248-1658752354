import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def sendmail(receiver,msg):
    message = Mail(
        from_email=os.environ.get('EMAIL_SENDER'),
        to_emails=receiver,
        subject='Expense tracker',
        body=msg)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
       
    except Exception as e:
        print(e.message)
    
    
    
    
