#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple email notification script using QQ SMTP server
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def send_email(sender_email, sender_password, receiver_email, subject, body, port=465):
    """
    Send email using QQ SMTP server with SSL
    
    Args:
        sender_email: Sender's QQ email address
        sender_password: QQ email authorization code
        receiver_email: Receiver's email address
        subject: Email subject
        body: Email body content
        port: SMTP port (465 or 587), default is 465
    """
    try:
        # Create message
        message = MIMEMultipart()
        message['From'] = Header(sender_email)
        message['To'] = Header(receiver_email)
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Connect and send
        if port == 465:
            server = smtplib.SMTP_SSL('smtp.qq.com', port)
        else:
            server = smtplib.SMTP('smtp.qq.com', port)
            server.starttls()
        
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [receiver_email], message.as_string())
        server.quit()
        
        print(f"Email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Get credentials from environment variables
    MAILTO = os.getenv('MAILTO')
    MAIL_PASSWD = os.getenv('MAIL_PASSWD')
    
    if not MAILTO or not MAIL_PASSWD:
        print("Error: MAILTO and MAIL_PASSWD environment variables must be set")
        exit(1)
    
    # Get subject and body from command line arguments
    if len(sys.argv) < 3:
        print("Usage: python send_notification.py <subject> <body>")
        exit(1)
    
    subject = sys.argv[1]
    body = sys.argv[2]
    
    # Send email to yourself
    send_email(
        sender_email=MAILTO,
        sender_password=MAIL_PASSWD,
        receiver_email=MAILTO,
        subject=subject,
        body=body,
        port=465  # Use 465 (SSL) or 587 (STARTTLS)
    )
