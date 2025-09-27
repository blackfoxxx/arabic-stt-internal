"""
Email service for notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


async def send_verification_email(email: str, name: str, token: str) -> bool:
    """Send email verification email"""
    
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email verification")
        return True  # Don't fail if SMTP not configured
    
    try:
        # Create verification URL
        verification_url = f"https://{settings.DOMAIN_NAME or 'localhost:3000'}/auth/verify-email?token={token}"
        
        # Email content in Arabic
        subject = "تأكيد عنوان البريد الإلكتروني - منصة التفريغ الصوتي العربية"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; text-align: right; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .button {{ background: #1e40af; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>منصة التفريغ الصوتي العربية</h1>
                </div>
                <div class="content">
                    <h2>مرحباً {name}،</h2>
                    <p>شكراً لك على التسجيل في منصة التفريغ الصوتي العربية.</p>
                    <p>للمتابعة، يرجى تأكيد عنوان بريدك الإلكتروني بالنقر على الرابط أدناه:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" class="button">تأكيد البريد الإلكتروني</a>
                    </p>
                    <p>إذا لم تقم بإنشاء هذا الحساب، يرجى تجاهل هذا البريد.</p>
                    <p>مع تحياتنا،<br>فريق منصة التفريغ الصوتي العربية</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await _send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error("Failed to send verification email", email=email, error=str(e))
        return False


async def send_password_reset_email(email: str, name: str, token: str) -> bool:
    """Send password reset email"""
    
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping password reset email")
        return True
    
    try:
        # Create reset URL
        reset_url = f"https://{settings.DOMAIN_NAME or 'localhost:3000'}/auth/reset-password?token={token}"
        
        subject = "إعادة تعيين كلمة المرور - منصة التفريغ الصوتي العربية"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; text-align: right; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc2626, #ef4444); color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .button {{ background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>إعادة تعيين كلمة المرور</h1>
                </div>
                <div class="content">
                    <h2>مرحباً {name}،</h2>
                    <p>تلقينا طلباً لإعادة تعيين كلمة المرور لحسابك.</p>
                    <p>لإعادة تعيين كلمة المرور، انقر على الرابط أدناه:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="button">إعادة تعيين كلمة المرور</a>
                    </p>
                    <div class="warning">
                        <strong>تنبيه:</strong> هذا الرابط صالح لمدة ساعة واحدة فقط.
                    </div>
                    <p>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد.</p>
                    <p>مع تحياتنا،<br>فريق منصة التفريغ الصوتي العربية</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await _send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error("Failed to send password reset email", email=email, error=str(e))
        return False


async def send_job_completion_email(
    email: str, 
    name: str, 
    job_id: str, 
    transcript_id: str,
    media_filename: str
) -> bool:
    """Send job completion notification email"""
    
    if not settings.SMTP_HOST:
        return True
    
    try:
        transcript_url = f"https://{settings.DOMAIN_NAME or 'localhost:3000'}/transcripts/{transcript_id}"
        
        subject = f"اكتمل تفريغ الملف: {media_filename}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; text-align: right; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669, #10b981); color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .button {{ background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }}
                .success {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 6px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ اكتمل التفريغ الصوتي</h1>
                </div>
                <div class="content">
                    <h2>مرحباً {name}،</h2>
                    <div class="success">
                        <strong>تم بنجاح!</strong> اكتمل تفريغ الملف الصوتي الخاص بك.
                    </div>
                    <p><strong>اسم الملف:</strong> {media_filename}</p>
                    <p><strong>رقم المهمة:</strong> {job_id}</p>
                    <p>يمكنك الآن مراجعة وتحرير النص المفرغ:</p>
                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{transcript_url}" class="button">مراجعة النص المفرغ</a>
                    </p>
                    <p>الميزات المتاحة:</p>
                    <ul>
                        <li>تحرير النص مباشرة</li>
                        <li>تسمية المتحدثين</li>
                        <li>تصدير بصيغ متعددة</li>
                        <li>مشاركة مع الفريق</li>
                    </ul>
                    <p>مع تحياتنا،<br>فريق منصة التفريغ الصوتي العربية</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await _send_email(email, subject, html_content)
        
    except Exception as e:
        logger.error("Failed to send job completion email", email=email, error=str(e))
        return False


async def _send_email(email: str, subject: str, html_content: str) -> bool:
    """Send email using configured SMTP"""
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = email
        
        # Add HTML content
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)
        
        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        if settings.SMTP_USE_TLS:
            server.starttls()
        
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(settings.FROM_EMAIL, email, text)
        server.quit()
        
        logger.info("Email sent successfully", to=email, subject=subject)
        return True
        
    except Exception as e:
        logger.error("Failed to send email", to=email, error=str(e))
        return False