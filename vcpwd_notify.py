#!/usr/bin/env python 
import pexpect
import smtplib
import subprocess
import os
import time
import email.utils
from email.mime.text import MIMEText
from email.header import Header

sso_user = {'username': 'email_name'}

chpwlist = []

def send_mail(reciver, msg):
    mail_host = 'host_ip'
    mail_port = 25

    sender = 'sender_email'
    subject = "vCenter Account Password Expiry Notification"

    sso_user_key = reciver.strip().split(':')[1].lstrip()
    #print('recv: ', reciver)
    message = MIMEText("vCenter website {0} password will expire in {1}.".format(reciver, msg), 'html')
    reciver = ''.join((sso_user[sso_user_key], "@email.domain.com"))
    message['From'] = email.utils.formataddr(('email_alias',sender))
    message['To'] = email.utils.formataddr((reciver,reciver))
    message['Subject'] = Header(subject)

    try:
        ms = smtplib.SMTP(mail_host, mail_port)
        #ms.set_debuglevel(True)
        ms.sendmail(sender, reciver, message.as_string())
    except:
        os._exit(0)
    finally:
        ms.quit()
    
    
def user_pwd_info(account):
    cmd = '/usr/lib/vmware-vmafd/bin/dir-cli user find-by-name --account {0} --level 2'
    child = pexpect.spawnu(cmd.format(account), timeout=30)
    child.expect('\w.*password.*')
    child.sendline('PASSWORD')
    child.expect(pexpect.EOF)
    tmplist = child.before.strip().split('\r\n')
 
    if 'expired' not in tmplist[6]:
        chpwlist.append(tmplist)

def main():
    mail_recv_dict = {}
    for key in sso_user:
        user_pwd_info(key)
    #print('chpwlist: ', chpwlist)

    for i in range(len(chpwlist)):
        expire_day_list = chpwlist[i][6].strip().split('day(s)')
        expire_day_user = chpwlist[i][0].strip()
        #print(expire_day_list)
        #print(expire_day_user)
        if len(expire_day_list) == 2:
            if int(expire_day_list[0].strip().split(':')[1]) <= 14:
                mail_recv_dict[expire_day_user] = chpwlist[i][6].strip().split(':')[1]
                #print(chpwlist[i][0])
                #print(int(expire_day_list[0].strip().split(':')[1]))

    if mail_recv_dict:
        for key in mail_recv_dict:
            send_mail(key, mail_recv_dict[key])
    else:
        print('false dict: ', len(mail_recv_dict))

if __name__ == '__main__':
    main()
