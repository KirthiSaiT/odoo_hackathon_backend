"""
Email Service Module
Handles sending verification and password reset emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending transactional emails"""
    
    @staticmethod
    def _get_smtp_connection():
        """Create SMTP connection"""
        settings = get_settings()
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        return server
    
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email via SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
        
        Returns:
            True if sent successfully, False otherwise
        """
        settings = get_settings()
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            msg["To"] = to_email
            
            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)
            
            with EmailService._get_smtp_connection() as server:
                server.sendmail(
                    settings.SMTP_FROM_EMAIL,
                    to_email,
                    msg.as_string()
                )
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_email(to_email: str, name: str, token: str) -> bool:
        """
        Send email verification link
        
        Args:
            to_email: User's email address
            name: User's name
            token: Verification token
        
        Returns:
            True if sent successfully
        """
        settings = get_settings()
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; border: 1px solid #e91e63; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <h1 style="color: #e91e63; margin: 0; font-size: 28px; font-weight: 700;">
                                        Verify Your Email
                                    </h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px 40px 40px;">
                                    <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Hello <strong style="color: #e91e63;">{name}</strong>,
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Thank you for signing up! Please verify your email address by clicking the button below.
                                    </p>
                                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);">
                                                <a href="{verification_link}" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600;">
                                                    Verify Email Address
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="color: #666666; font-size: 12px; line-height: 1.6; margin: 30px 0 0 0; text-align: center;">
                                        This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.
                                    </p>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: rgba(0,0,0,0.3); text-align: center;">
                                    <p style="color: #666666; font-size: 12px; margin: 0;">
                                        © 2026 SaaS Auth Module. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return EmailService._send_email(
            to_email,
            "Verify Your Email Address",
            html_content
        )
    
    @staticmethod
    def send_password_reset_email(to_email: str, name: str, token: str) -> bool:
        """
        Send password reset link
        
        Args:
            to_email: User's email address
            name: User's name
            token: Reset token
        
        Returns:
            True if sent successfully
        """
        settings = get_settings()
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; border: 1px solid #e91e63; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <h1 style="color: #e91e63; margin: 0; font-size: 28px; font-weight: 700;">
                                        Reset Your Password
                                    </h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px 40px 40px;">
                                    <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Hello <strong style="color: #e91e63;">{name}</strong>,
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        We received a request to reset your password. Click the button below to create a new password.
                                    </p>
                                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);">
                                                <a href="{reset_link}" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600;">
                                                    Reset Password
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="color: #666666; font-size: 12px; line-height: 1.6; margin: 30px 0 0 0; text-align: center;">
                                        This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
                                    </p>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: rgba(0,0,0,0.3); text-align: center;">
                                    <p style="color: #666666; font-size: 12px; margin: 0;">
                                        © 2026 SaaS Auth Module. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return EmailService._send_email(
            to_email,
            "Reset Your Password",
            html_content
        )

    @staticmethod
    def send_overdue_reminder(to_email: str, client_name: str, amount: float, due_date: datetime) -> bool:
        """
        Send payment overdue reminder email
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; border: 1px solid #e91e63; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <h1 style="color: #e91e63; margin: 0; font-size: 28px; font-weight: 700;">
                                        Payment Reminder
                                    </h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px 40px 40px;">
                                    <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Hello <strong style="color: #e91e63;">{client_name}</strong>,
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        This is a reminder that your payment of <strong style="color: #ffffff;">${amount}</strong> was due on <strong style="color: #ffffff;">{due_date}</strong>.
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Please make a payment as soon as possible to avoid any service interruption.
                                    </p>
                                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);">
                                                <a href="#" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600;">
                                                    Make Payment Now
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: rgba(0,0,0,0.3); text-align: center;">
                                    <p style="color: #666666; font-size: 12px; margin: 0;">
                                        © 2026 SaaS Auth Module. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return EmailService._send_email(
            to_email,
            "Urgent: Payment Overdue Notification",
            html_content
        )

    @staticmethod
    def send_welcome_email(to_email: str, name: str, password: str, product_name: str = "N/A", amount: float = 0.0, frequency: str = "N/A", start_date: str = "N/A", reset_token: str = None) -> bool:
        """
        Send welcome email with credentials, billing info, and reset link
        """
        settings = get_settings()
        login_link = f"{settings.FRONTEND_URL}/login"
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}" if reset_token else None
        
        billing_html = f"""
        <div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(76, 175, 80, 0.2);">
            <h3 style="color: #4caf50; margin-top: 0;">Subscription Summary</h3>
            <p style="color: #ffffff; margin: 0 0 5px 0;"><strong>Product:</strong> {product_name}</p>
            <p style="color: #ffffff; margin: 0 0 5px 0;"><strong>Agreed Amount:</strong> ${amount:,.2f}</p>
            <p style="color: #ffffff; margin: 0 0 5px 0;"><strong>Frequency:</strong> {frequency}</p>
            <p style="color: #ffffff; margin: 0;"><strong>Start Date:</strong> {start_date}</p>
        </div>
        """ if product_name != "N/A" else ""

        reset_button = f"""
        <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 20px auto;">
            <tr>
                <td style="border-radius: 8px; background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);">
                    <a href="{reset_link}" target="_blank" style="display: inline-block; padding: 12px 30px; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 600;">
                        Secure Your Account (Reset Password)
                    </a>
                </td>
            </tr>
        </table>
        """ if reset_link else ""

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; border: 1px solid #4caf50; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <h1 style="color: #4caf50; margin: 0; font-size: 28px; font-weight: 700;">
                                        Welcome to SaaS Platform
                                    </h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px 40px 40px;">
                                    <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Hello <strong style="color: #4caf50;">{name}</strong>,
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Your account has been successfully created. We are excited to have you on board!
                                    </p>
                                    
                                    {billing_html}

                                    <div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                                        <p style="color: #ffffff; margin: 0 0 10px 0;"><strong>Email:</strong> {to_email}</p>
                                        <p style="color: #ffffff; margin: 0;"><strong>Temporary Password:</strong> {password}</p>
                                    </div>

                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 20px 0;">
                                        For security, we recommend you set your own password immediately using the link below:
                                    </p>

                                    {reset_button}

                                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);">
                                                <a href="{login_link}" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600;">
                                                    Login to Portal
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: rgba(0,0,0,0.3); text-align: center;">
                                    <p style="color: #666666; font-size: 12px; margin: 0;">
                                        © 2026 SaaS Auth Module. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return EmailService._send_email(
            to_email,
            "Welcome to SaaS Platform - Your Account Details",
            html_content
        )

    @staticmethod
    def send_new_password_email(to_email: str, name: str, password: str) -> bool:
        """
        Send email with new password after admin reset
        """
        settings = get_settings()
        login_link = f"{settings.FRONTEND_URL}/login"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0a;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0a0a0a; padding: 40px 20px;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; border: 1px solid #ff9800; overflow: hidden;">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <h1 style="color: #ff9800; margin: 0; font-size: 28px; font-weight: 700;">
                                        Password Reset
                                    </h1>
                                </td>
                            </tr>
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px 40px 40px;">
                                    <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Hello <strong style="color: #ff9800;">{name}</strong>,
                                    </p>
                                    <p style="color: #b0b0b0; font-size: 14px; line-height: 1.6; margin: 0 0 30px 0;">
                                        Your password has been reset by an administrator. Here are your new credentials:
                                    </p>
                                    <div style="background-color: rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 30px;">
                                        <p style="color: #ffffff; margin: 0 0 10px 0;"><strong>Email:</strong> {to_email}</p>
                                        <p style="color: #ffffff; margin: 0;"><strong>New Password:</strong> {password}</p>
                                    </div>
                                    <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 8px; background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);">
                                                <a href="{login_link}" target="_blank" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600;">
                                                    Login with New Password
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="color: #666666; font-size: 12px; line-height: 1.6; margin: 30px 0 0 0; text-align: center;">
                                        Please change your password after logging in for security.
                                    </p>
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 20px 40px; background-color: rgba(0,0,0,0.3); text-align: center;">
                                    <p style="color: #666666; font-size: 12px; margin: 0;">
                                        © 2026 SaaS Auth Module. All rights reserved.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return EmailService._send_email(
            to_email,
            "Your Password Has Been Reset",
            html_content
        )
