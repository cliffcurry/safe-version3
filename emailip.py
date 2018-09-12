import smtplib from email.mime.text
import MIMEText
import datetime
import subprocess

ip = subprocess.check_output(['hostname', '-I'])
to = 'My email address'
gmail_user = 'Gmail used to send from'
gmail_password = 'Password'

smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo()
smtpserver.login(gmail_user, gmail_password)

today = datetime.date.today()
my_msg = '%s' % today.strftime('%b %d %Y')
msg = MIMEText(my_msg)
msg['Subject'] = 'Raspberry Pi IP: %s' % ip[:-2].decode("UTF-8")
msg['From'] = gmail_user
msg['To'] = to
smtpserver.sendmail(gmail_user, [to], msg.as_string())
smtpserver.quit()