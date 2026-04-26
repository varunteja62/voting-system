import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_otp_email(to_email, otp):
    """Send OTP email using SMTP settings from config"""
    try:
        smtp_server = current_app.config['SMTP_SERVER']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_user = current_app.config['SMTP_USERNAME']
        smtp_password = current_app.config['SMTP_PASSWORD']
        sender_email = current_app.config['MAIL_DEFAULT_SENDER']

        if not all([smtp_server, smtp_user, smtp_password]):
            print(f"SMTP settings not fully configured. OTP for {to_email} is: {otp}")
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = "NyayaVote Password Recovery OTP"
        message["From"] = sender_email
        message["To"] = to_email

        text = f"Your OTP for password recovery is: {otp}. This code expires in 10 minutes."
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
              <h2 style="color: #2563eb; text-align: center;">NyayaVote Security</h2>
              <p>Hello,</p>
              <p>We received a request to reset your password. Use the following One-Time Password (OTP) to proceed:</p>
              <div style="text-align: center; margin: 30px 0; padding: 15px; background: #f8fafc; border-radius: 8px; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #1e40af;">
                {otp}
              </div>
              <p>This OTP is valid for <strong>10 minutes</strong>. If you did not request this, please ignore this email.</p>
              <hr style="border: 0; border-top: 1px solid #e0e0e0; margin: 20px 0;">
              <p style="font-size: 12px; color: #666; text-align: center;">NyayaVote - Secure Digital Voting Platform</p>
            </div>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, to_email, message.as_string())
        
        print(f"OTP email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        print(f"FALLBACK: OTP for {to_email} is: {otp}")
        return False
