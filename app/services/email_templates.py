"""Email templates for prayer reminders and notifications.

This module contains HTML email templates for various types of notifications
including prayer reminders, consistency nudges, and completion confirmations.
"""

from datetime import datetime
from typing import Optional

from app.models.user import User


def get_prayer_reminder_template(user: User, prayer_type: str, prayer_time: datetime,
                                verse: Optional[dict], hadith: Optional[dict],
                                completion_link: str) -> str:
    """Get prayer reminder email template."""
    _ = get_prayer_name_arabic(prayer_type)
    _ = get_prayer_name_english(prayer_type)

    # Use user's language preference
    if user.language == 'en':
        return get_english_prayer_reminder_template(user, prayer_type, prayer_time, verse, hadith, completion_link)
    return get_arabic_prayer_reminder_template(user, prayer_type, prayer_time, verse, hadith, completion_link)


def get_arabic_prayer_reminder_template(user: User, prayer_type: str, prayer_time: datetime,
                                       verse: Optional[dict], hadith: Optional[dict],
                                       completion_link: str) -> str:
    """Get Arabic prayer reminder email template."""
    prayer_name_arabic = get_prayer_name_arabic(prayer_type)

    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تذكير صلاة {prayer_name_arabic}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .prayer-time {{ background: #E8F5E8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .verse {{ background: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0; border-right: 4px solid #FF9800; }}
            .hadith {{ background: #E3F2FD; padding: 20px; border-radius: 8px; margin: 20px 0; border-right: 4px solid #2196F3; }}
            .completion-link {{ text-align: center; margin: 30px 0; }}
            .btn {{ display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .arabic {{ font-size: 18px; line-height: 1.8; }}
            .english {{ font-size: 14px; color: #666; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕌 تذكير صلاة {prayer_name_arabic}</h1>
                <p>السلام عليكم ورحمة الله وبركاته</p>
            </div>

            <div class="content">
                <p>عزيزي/عزيزتي {user.first_name}،</p>

                <div class="prayer-time">
                    <h2>⏰ وقت صلاة {prayer_name_arabic}</h2>
                    <p style="font-size: 24px; font-weight: bold; color: #2E7D32;">
                        {prayer_time.strftime('%H:%M')}
                    </p>
                    <p>{prayer_time.strftime('%A, %B %d, %Y')}</p>
                </div>

                {f'''
                <div class="verse">
                    <h3>📖 آية قرآنية</h3>
                    <div class="arabic">{verse['arabic_text']}</div>
                    <div class="english">{verse['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{verse['surah_name_english']} {verse['surah_number']}:{verse['verse_number']}</p>
                </div>
                ''' if verse else ''}

                {f'''
                <div class="hadith">
                    <h3>💬 حديث شريف</h3>
                    <div class="arabic">{hadith['arabic_text']}</div>
                    <div class="english">{hadith['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{hadith['collection']} {hadith['hadith_number']}</p>
                </div>
                ''' if hadith else ''}

                <div class="completion-link">
                    <p>اضغط على الرابط أدناه لتأكيد أداء الصلاة:</p>
                    <a href="{completion_link}" class="btn">✅ أكدت أداء الصلاة</a>
                </div>

                <p style="margin-top: 30px;">
                    <strong>تذكير:</strong> هذا الرابط صالح لمدة ساعتين بعد وقت الصلاة.
                </p>
            </div>

            <div class="footer">
                <p>تم إرسال هذا التذكير من تطبيق SalahTracker</p>
                <p>لإيقاف التذكيرات، يمكنك تعديل إعدادات الإشعارات في حسابك</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_consistency_nudge_template(user: User, verse: Optional[dict],
                                  hadith: Optional[dict], frontend_url: str = "https://salah-tracker.com") -> str:
    """Get consistency nudge email template."""
    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>دعنا نعود إلى المسار الصحيح</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #FF9800, #FFC107); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .motivation {{ background: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0; border-right: 4px solid #FF9800; }}
            .verse {{ background: #E8F5E8; padding: 20px; border-radius: 8px; margin: 20px 0; border-right: 4px solid #4CAF50; }}
            .hadith {{ background: #E3F2FD; padding: 20px; border-radius: 8px; margin: 20px 0; border-right: 4px solid #2196F3; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .arabic {{ font-size: 18px; line-height: 1.8; }}
            .english {{ font-size: 14px; color: #666; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💪 دعنا نعود إلى المسار الصحيح</h1>
                <p>السلام عليكم ورحمة الله وبركاته</p>
            </div>

            <div class="content">
                <p>عزيزي/عزيزتي {user.first_name}،</p>

                <div class="motivation">
                    <h2>🌟 رسالة تشجيعية</h2>
                    <p>لاحظنا أنك لم تؤد بعض الصلوات مؤخراً. لا تقلق، هذا يحدث للجميع! المهم هو أن نعود إلى المسار الصحيح.</p>
                    <p>الله تعالى يحب التائبين، وكل خطوة نحو الصلاة هي خطوة نحو رضاه.</p>
                </div>

                {f'''
                <div class="verse">
                    <h3>📖 آية قرآنية</h3>
                    <div class="arabic">{verse['arabic_text']}</div>
                    <div class="english">{verse['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{verse['surah_name_english']} {verse['surah_number']}:{verse['verse_number']}</p>
                </div>
                ''' if verse else ''}

                {f'''
                <div class="hadith">
                    <h3>💬 حديث شريف</h3>
                    <div class="arabic">{hadith['arabic_text']}</div>
                    <div class="english">{hadith['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{hadith['collection']} {hadith['hadith_number']}</p>
                </div>
                ''' if hadith else ''}

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}"
                       style="display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        🕌 ابدأ من جديد
                    </a>
                </div>
            </div>

            <div class="footer">
                <p>نحن هنا لمساعدتك في الحفاظ على صلواتك</p>
                <p>تطبيق SalahTracker</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_prayer_name_arabic(prayer_type: str) -> str:
    """Get Arabic name for prayer type."""
    prayer_names = {
        'fajr': 'الفجر',
        'dhuhr': 'الظهر',
        'asr': 'العصر',
        'maghrib': 'المغرب',
        'isha': 'العشاء'
    }
    return prayer_names.get(prayer_type, prayer_type)


def get_prayer_name_english(prayer_type: str) -> str:
    """Get English name for prayer type."""
    prayer_names = {
        'fajr': 'Fajr',
        'dhuhr': 'Dhuhr',
        'asr': 'Asr',
        'maghrib': 'Maghrib',
        'isha': 'Isha'
    }
    return prayer_names.get(prayer_type, prayer_type.title())


def get_english_prayer_reminder_template(user: User, prayer_type: str, prayer_time: datetime,
                                        verse: Optional[dict], hadith: Optional[dict],
                                        completion_link: str) -> str:
    """Get English prayer reminder email template."""
    prayer_name_english = get_prayer_name_english(prayer_type)

    return f"""
    <!DOCTYPE html>
    <html dir="ltr" lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{prayer_name_english} Prayer Reminder</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .prayer-time {{ background: #E8F5E8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            .verse {{ background: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FF9800; }}
            .hadith {{ background: #E3F2FD; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196F3; }}
            .completion-link {{ text-align: center; margin: 30px 0; }}
            .btn {{ display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .arabic {{ font-size: 18px; line-height: 1.8; text-align: right; }}
            .english {{ font-size: 16px; color: #333; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕌 {prayer_name_english} Prayer Reminder</h1>
                <p>Peace be upon you and Allah's mercy and blessings</p>
            </div>

            <div class="content">
                <p>Dear {user.first_name or user.username},</p>

                <div class="prayer-time">
                    <h2>⏰ {prayer_name_english} Prayer Time</h2>
                    <p style="font-size: 24px; font-weight: bold; color: #2E7D32;">
                        {prayer_time.strftime('%H:%M')}
                    </p>
                    <p>{prayer_time.strftime('%A, %B %d, %Y')}</p>
                </div>

                {f'''
                <div class="verse">
                    <h3>📖 Quranic Verse</h3>
                    <div class="arabic">{verse['arabic_text']}</div>
                    <div class="english">{verse['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{verse['surah_name_english']} {verse['surah_number']}:{verse['verse_number']}</p>
                </div>
                ''' if verse else ''}

                {f'''
                <div class="hadith">
                    <h3>💬 Hadith</h3>
                    <div class="arabic">{hadith['arabic_text']}</div>
                    <div class="english">{hadith['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{hadith['collection']} {hadith['hadith_number']}</p>
                </div>
                ''' if hadith else ''}

                <div class="completion-link">
                    <p>Click the link below to confirm you have performed the prayer:</p>
                    <a href="{completion_link}" class="btn">✅ I have performed the prayer</a>
                </div>

                <p style="margin-top: 30px;">
                    <strong>Reminder:</strong> This link is valid for 2 hours after the prayer time.
                </p>
            </div>

            <div class="footer">
                <p>This reminder was sent from SalahTracker app</p>
                <p>To stop reminders, you can modify your notification settings in your account</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_prayer_window_reminder_template(user: User, prayer_type: str, prayer_time: datetime,
                                       verse: Optional[dict], hadith: Optional[dict],
                                       completion_link: str, end_time: str) -> str:
    """Get prayer window reminder email template."""
    _ = get_prayer_name_english(prayer_type)

    # Use user's language preference
    if user.language == 'en':
        return get_english_prayer_window_reminder_template(user, prayer_type, prayer_time, verse, hadith, completion_link, end_time)
    return get_arabic_prayer_reminder_template(user, prayer_type, prayer_time, verse, hadith, completion_link)


def get_english_prayer_window_reminder_template(user: User, prayer_type: str, prayer_time: datetime,
                                               verse: Optional[dict], hadith: Optional[dict],
                                               completion_link: str, end_time: str) -> str:
    """Get English prayer window reminder email template."""
    prayer_name_english = get_prayer_name_english(prayer_type)

    return f"""
    <!DOCTYPE html>
    <html dir="ltr" lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{prayer_name_english} Prayer Window Open</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 30px; }}
            .prayer-window {{ background: #E8F5E8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; border: 2px solid #4CAF50; }}
            .urgency {{ background: #FFF3E0; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FF9800; }}
            .verse {{ background: #FFF3E0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FF9800; }}
            .hadith {{ background: #E3F2FD; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2196F3; }}
            .completion-link {{ text-align: center; margin: 30px 0; }}
            .btn {{ display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            .arabic {{ font-size: 18px; line-height: 1.8; text-align: right; }}
            .english {{ font-size: 16px; color: #333; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕌 {prayer_name_english} Prayer Window Open</h1>
                <p>Time to perform your prayer!</p>
            </div>

            <div class="content">
                <p>Dear {user.first_name or user.username},</p>

                <div class="urgency">
                    <h2>⏰ Prayer Time is Now Active!</h2>
                    <p>The time window for {prayer_name_english} prayer is now open. Please perform your prayer as soon as possible.</p>
                </div>

                <div class="prayer-window">
                    <h2>🕐 Prayer Time Window</h2>
                    <p style="font-size: 24px; font-weight: bold; color: #2E7D32;">
                        {prayer_time.strftime('%H:%M')} - {end_time}
                    </p>
                    <p>{prayer_time.strftime('%A, %B %d, %Y')}</p>
                    <p style="color: #d32f2f; font-weight: bold;">⏳ Don't miss this prayer!</p>
                </div>

                {f'''
                <div class="verse">
                    <h3>📖 Quranic Verse</h3>
                    <div class="arabic">{verse['arabic_text']}</div>
                    <div class="english">{verse['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{verse['surah_name_english']} {verse['surah_number']}:{verse['verse_number']}</p>
                </div>
                ''' if verse else ''}

                {f'''
                <div class="hadith">
                    <h3>💬 Hadith</h3>
                    <div class="arabic">{hadith['arabic_text']}</div>
                    <div class="english">{hadith['english_translation']}</div>
                    <p style="font-size: 12px; color: #999; margin-top: 10px;">{hadith['collection']} {hadith['hadith_number']}</p>
                </div>
                ''' if hadith else ''}

                <div class="completion-link">
                    <p><strong>After performing your prayer, click below to mark it as complete:</strong></p>
                    <a href="{completion_link}" class="btn">✅ Mark Prayer as Complete</a>
                </div>

                <p style="margin-top: 30px;">
                    <strong>Important:</strong> This prayer window will close at {end_time}. Please complete your prayer before then.
                </p>
            </div>

            <div class="footer">
                <p>This window reminder was sent from SalahTracker app</p>
                <p>To stop reminders, you can modify your notification settings in your account</p>
            </div>
        </div>
    </body>
    </html>
    """

