# ==========================================
# Code Generator Bot
# Main File (v1.2 - Fixed & Improved)
# ==========================================

import os
import html

import telebot
from telebot import types

from config import (
    BOT_TOKEN,
    ADMIN_ID,
    CONTACT_USERNAME,
    BOT_NAME,
    BOT_VERSION,
)

from database import (
    init_database,
    user_exists,
    add_user,
    get_users_count,
    get_projects_count,
    get_user_projects,
    add_project,
    update_project_name,
)

from generator import (
    start_project,
    get_session,
    save_idea,
    get_project_id,
    get_project_path,
    get_project_type,
    generation_complete,
    end_project,
    add_image,
)

from ai_client import generate
from ai_generator import build_prompt, parse_response
from project_writer import write_project
from zip_builder import create_zip

# ==========================================
# BOT
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)


# ==========================================
# DATABASE
# ==========================================

init_database()


# ==========================================
# ADMIN NOTIFICATION
# ==========================================

def notify_admin(text):
    if not ADMIN_ID:
        return
    try:
        bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except Exception as error:
        print("Admin notification error:", error)


# ==========================================
# RETRY MENU
# ==========================================

def retry_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "🔄 حاول تاني",
            callback_data="retry_generation",
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "❌ إلغاء المشروع",
            callback_data="cancel_project",
        )
    )
    return markup


# ==========================================
# AI PROJECT GENERATOR
# ==========================================

def generate_project_for_user(user_id, chat_id, project_type, idea):

    try:
        session = get_session(user_id)

        if not session:
            bot.send_message(chat_id, "❌ مش لاقي المشروع الحالي.")
            return False

        images = session.get("images", [])

        prompt = build_prompt(
            project_type=project_type,
            idea=idea,
            images=images,
        )

        bot.send_message(
            chat_id,
            "🧠 <b>جاري تحليل فكرتك...</b>\n\n"
            "⏳ Gemini بيجهز ملفات المشروع دلوقتي.",
            parse_mode="HTML",
        )

        result = generate(prompt)

        if not result["success"]:
            print("AI ERROR:", result["error"])
            bot.send_message(
                chat_id,
                "❌ حصل خطأ أثناء توليد المشروع.\n\n"
                "ممكن يكون ضغط على الـAPI. جرب تاني.",
                parse_mode="HTML",
                reply_markup=retry_menu(),
            )
            return False

        parsed = parse_response(result["text"])

        if not parsed["success"]:
            print("PARSE ERROR:", parsed["error"])
            bot.send_message(
                chat_id,
                "❌ Gemini رجّع نتيجة غير صالحة.\n\n"
                "دوس «حاول تاني» وحنعيد المحاولة.",
                parse_mode="HTML",
                reply_markup=retry_menu(),
            )
            return False

        project_path = get_project_path(user_id)

        bot.send_message(
            chat_id,
            "📁 <b>جاري إنشاء ملفات المشروع...</b>",
            parse_mode="HTML",
        )

        written = write_project(project_path, parsed["files"])

        if not written["success"]:
            print("WRITE ERROR:", written["error"])
            bot.send_message(
                chat_id,
                "❌ حصل خطأ أثناء إنشاء الملفات.",
                parse_mode="HTML",
                reply_markup=retry_menu(),
            )
            return False

        # Update project name in database with AI-generated name
        project_name = parsed.get("project_name", "generated-project")
        update_project_name(project_path, project_name)

        bot.send_message(
            chat_id,
            "📦 <b>جاري تجهيز المشروع...</b>",
            parse_mode="HTML",
        )

        zip_result = create_zip(project_path)

        if not zip_result["success"]:
            print("ZIP ERROR:", zip_result["error"])
            bot.send_message(
                chat_id,
                "❌ حصل خطأ أثناء إنشاء ملف ZIP.",
                parse_mode="HTML",
                reply_markup=retry_menu(),
            )
            return False

        safe_name = html.escape(str(project_name))
        zip_path = zip_result["path"]

        with open(zip_path, "rb") as zip_file:
            bot.send_document(
                chat_id,
                zip_file,
                caption=(
                    "🎉 <b>تم إنشاء مشروعك!</b>\n\n"
                    f"📦 <b>{safe_name}</b>\n\n"
                    f"📁 عدد الملفات: "
                    f"<b>{len(written['files'])}</b>\n\n"
                    "🚀 المشروع جاهز للتحميل."
                ),
                parse_mode="HTML",
            )

        generation_complete(user_id)

        notify_admin(
            "🎉 <b>تم إنشاء مشروع بنجاح!</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📦 Project: <b>{safe_name}</b>\n"
            f"📁 Files: <b>{len(written['files'])}</b>"
        )

        return True

    except Exception as error:
        print("PROJECT GENERATOR ERROR:", error)
        bot.send_message(
            chat_id,
            "❌ حصل خطأ غير متوقع أثناء إنشاء المشروع.",
            parse_mode="HTML",
            reply_markup=retry_menu(),
        )
        return False


# ==========================================
# USER INFO
# ==========================================

def get_user_info(user):
    username = f"@{user.username}" if user.username else "بدون Username"
    first_name = user.first_name if user.first_name else "غير معروف"
    return (
        f"👤 <b>الاسم:</b> {html.escape(first_name)}\n"
        f"🔗 <b>Username:</b> {html.escape(username)}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>"
    )


# ==========================================
# MAIN MENU
# ==========================================

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(
            "🌐 إنشاء موقع",
            callback_data="create_website",
        ),
        types.InlineKeyboardButton(
            "🤖 إنشاء بوت",
            callback_data="create_bot",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "📂 مشاريعي",
            callback_data="projects",
        ),
        types.InlineKeyboardButton(
            "📊 إحصائياتي",
            callback_data="stats",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "⚙️ الإعدادات",
            callback_data="settings",
        ),
        types.InlineKeyboardButton(
            "📚 المساعدة",
            callback_data="help",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "👨‍💻 تواصل معنا",
            url=f"https://t.me/{CONTACT_USERNAME}",
        )
    )
    return markup


# ==========================================
# SETTINGS MENU
# ==========================================

def settings_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(
            "🌐 لغة البرمجة",
            callback_data="setting_programming",
        ),
        types.InlineKeyboardButton(
            "🎨 شكل الأكواد",
            callback_data="setting_style",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "📝 لغة الردود",
            callback_data="setting_language",
        ),
        types.InlineKeyboardButton(
            "📦 إعدادات ZIP",
            callback_data="setting_zip",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "🔔 الإشعارات",
            callback_data="setting_notifications",
        ),
        types.InlineKeyboardButton(
            "🗑️ حذف بياناتي",
            callback_data="delete_data",
        ),
    )
    markup.add(
        types.InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="back_main",
        )
    )
    return markup


# ==========================================
# IMAGE MENU
# ==========================================

def finish_images_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "✅ خلصت الصور",
            callback_data="finish_images",
        )
    )
    return markup


# ==========================================
# /START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    user = message.from_user
    is_new = not user_exists(user.id)

    if is_new:
        add_user(
            user.id,
            user.username if user.username else "",
            user.first_name if user.first_name else "",
        )
        notify_admin(
            "🚨 <b>مستخدم جديد دخل البوت!</b>\n\n"
            + get_user_info(user)
            + "\n\n🎉 مرحبًا بالمستخدم الجديد!"
        )

    bot.send_message(
        message.chat.id,
        f"🤖 <b>{BOT_NAME}</b>\n\n"
        "👋 أهلاً بيك!\n\n"
        "🚀 حوّل فكرتك إلى مشروع جاهز.\n\n"
        "اختار نوع المشروع اللي عايز تنشئه:",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# ==========================================
# /CANCEL
# ==========================================

@bot.message_handler(commands=["cancel"])
def cancel(message):

    session = get_session(message.from_user.id)

    if not session:
        bot.send_message(
            message.chat.id,
            "👋 مفيش مشروع شغال أصلًا.",
            reply_markup=main_menu(),
        )
        return

    end_project(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "❌ <b>تم إلغاء المشروع الحالي.</b>\n\n"
        "تقدر تبدأ مشروع جديد في أي وقت.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# ==========================================
# /STATS (ADMIN ONLY)
# ==========================================

@bot.message_handler(commands=["stats"])
def admin_stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمين: <b>{get_users_count()}</b>\n"
        f"📦 المشاريع: <b>{get_projects_count()}</b>",
        parse_mode="HTML",
    )


# ==========================================
# TEXT MESSAGE HANDLER
# ==========================================

@bot.message_handler(content_types=["text"])
def handle_text(message):

    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    session = get_session(user_id)

    if not session:
        bot.send_message(
            message.chat.id,
            "👋 مفيش مشروع شغال حاليًا.\n\n"
            "اختار من القائمة الرئيسية نوع المشروع اللي عايز تعمله.",
            reply_markup=main_menu(),
        )
        return

    # IDEA STEP
    if session["step"] == "idea":
        idea = message.text.strip()

        if len(idea) < 10:
            bot.send_message(
                message.chat.id,
                "⚠️ الفكرة قصيرة جدًا.\n\n"
                "اكتب تفاصيل أكتر عن المشروع عشان نقدر نطلع نتيجة أفضل.",
            )
            return

        save_idea(user_id, idea)

        project_id = get_project_id(user_id)
        project_type = get_project_type(user_id)

        if project_type == "website":
            project_title = "🌐 موقع"
        else:
            project_title = "🤖 Telegram Bot"

        notify_admin(
            "📝 <b>فكرة مشروع جديدة</b>\n\n"
            f"{get_user_info(message.from_user)}\n\n"
            f"📦 النوع: {project_title}\n"
            f"🆔 Project ID: <code>{project_id}</code>\n\n"
            f"💡 <b>الفكرة:</b>\n"
            f"{html.escape(idea)}"
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📸 إضافة صور",
                callback_data="add_images",
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "⏭️ تخطي الصور",
                callback_data="skip_images",
            )
        )

        bot.send_message(
            message.chat.id,
            "🔥 <b>تمام! استلمت فكرتك.</b>\n\n"
            f"🆔 Project ID: <code>{project_id}</code>\n\n"
            "📸 عندك صور أو Assets عايز تستخدمها في المشروع؟\n\n"
            "تقدر تبعت Logo أو صور الموقع أو أي ملفات محتاجها.",
            parse_mode="HTML",
            reply_markup=markup,
        )
        return

    # IMAGES STEP
    if session["step"] == "images":
        bot.send_message(
            message.chat.id,
            "📸 المرحلة الحالية: رفع الصور.\n\n"
            "ابعت الصور هنا أو اضغط «خلصت الصور» لما تخلص.",
            reply_markup=finish_images_menu(),
        )
        return

    # GENERATING STEP
    if session["step"] == "generating":
        bot.send_message(
            message.chat.id,
            "⏳ المشروع لسه بيتعمل...\n"
            "استنى شوية وهيوصلك الـZIP.",
        )
        return

    # COMPLETED STEP
    if session["step"] == "completed":
        bot.send_message(
            message.chat.id,
            "✅ مشروعك خلص واتبعت!\n\n"
            "تقدر تبدأ مشروع جديد دلوقتي.",
            reply_markup=main_menu(),
        )
        return


# ==========================================
# CALLBACK HANDLER
# ==========================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    chat_id = call.message.chat.id
    user = call.from_user
    user_id = user.id

    # CREATE WEBSITE
    if call.data == "create_website":
        bot.answer_callback_query(call.id)

        session = start_project(user_id, "website")
        project_id = session["project_id"]
        project_path = session["project_folder"]

        add_project(user_id, "website", "New Website", project_path)

        notify_admin(
            "🌐 <b>بدأ إنشاء موقع</b>\n\n"
            + get_user_info(user)
            + f"\n\n🆔 Project ID: <code>{project_id}</code>"
        )

        bot.send_message(
            chat_id,
            "🌐 <b>إنشاء موقع جديد</b>\n\n"
            "📝 اكتبلي فكرة الموقع بالتفصيل.\n\n"
            "💡 مثال:\n"
            "عايز Portfolio شخصي Dark Mode وفيه About وProjects "
            "وContact وAnimations ويكون Responsive.\n\n"
            "🔥 كل ما تكتب تفاصيل أكتر، هنقدر نطلع مشروع أفضل.\n\n"
            "❌ لو عايز تلغي: اكتب /cancel",
            parse_mode="HTML",
        )

    # CREATE BOT
    elif call.data == "create_bot":
        bot.answer_callback_query(call.id)

        session = start_project(user_id, "telegram_bot")
        project_id = session["project_id"]
        project_path = session["project_folder"]

        add_project(
            user_id, "telegram_bot", "New Telegram Bot", project_path
        )

        notify_admin(
            "🤖 <b>بدأ إنشاء بوت</b>\n\n"
            + get_user_info(user)
            + f"\n\n🆔 Project ID: <code>{project_id}</code>"
        )

        bot.send_message(
            chat_id,
            "🤖 <b>إنشاء Telegram Bot</b>\n\n"
            "📝 اكتبلي فكرة البوت بالتفصيل.\n\n"
            "💡 مثال:\n"
            "عايز بوت فيه قائمة أزرار، نظام مستخدمين، "
            "إحصائيات وأوامر للإدارة.\n\n"
            "🔥 كل ما تكتب تفاصيل أكتر، النتيجة هتكون أفضل.\n\n"
            "❌ لو عايز تلغي: اكتب /cancel",
            parse_mode="HTML",
        )

    # ADD IMAGES
    elif call.data == "add_images":
        bot.answer_callback_query(call.id)

        session = get_session(user_id)
        if not session:
            bot.send_message(chat_id, "❌ المشروع غير موجود.")
            return

        session["step"] = "images"

        bot.send_message(
            chat_id,
            "📸 <b>إضافة الصور والملفات</b>\n\n"
            "ابعتلي الصور اللي عايز تستخدمها في المشروع.\n\n"
            "📁 البوت هيحفظها تلقائيًا داخل:\n"
            "<code>images/</code>\n\n"
            "ممكن تبعت أكتر من صورة.\n\n"
            "لما تخلص اضغط الزرار ده 👇",
            parse_mode="HTML",
            reply_markup=finish_images_menu(),
        )

    # SKIP IMAGES
    elif call.data == "skip_images":
        bot.answer_callback_query(call.id)

        session = get_session(user_id)
        if not session:
            return

        session["step"] = "generating"

        bot.send_message(
            chat_id,
            "⏭️ <b>تم تخطي الصور.</b>\n\n"
            "🚀 هنبدأ إنشاء المشروع دلوقتي...",
            parse_mode="HTML",
        )

        generate_project_for_user(
            user_id=user_id,
            chat_id=chat_id,
            project_type=session["project_type"],
            idea=session["idea"],
        )

    # FINISH IMAGES
    elif call.data == "finish_images":
        bot.answer_callback_query(call.id)

        session = get_session(user_id)
        if not session:
            bot.send_message(chat_id, "❌ المشروع غير موجود.")
            return

        session["step"] = "generating"
        images_count = len(session["images"])

        notify_admin(
            "📸 <b>انتهى المستخدم من رفع الصور</b>\n\n"
            + get_user_info(user)
            + f"\n\n🆔 Project ID: <code>{session['project_id']}</code>\n"
            f"📸 عدد الصور: {images_count}"
        )

        bot.send_message(
            chat_id,
            "🔥 <b>تمام!</b>\n\n"
            f"📸 عدد الصور: <b>{images_count}</b>\n\n"
            "🧠 جاري تحليل فكرتك...\n"
            "📁 تجهيز الملفات...\n"
            "📦 وبعدها هجهز لك المشروع في ZIP.",
            parse_mode="HTML",
        )

        generate_project_for_user(
            user_id=user_id,
            chat_id=chat_id,
            project_type=session["project_type"],
            idea=session["idea"],
        )

    # RETRY GENERATION
    elif call.data == "retry_generation":
        bot.answer_callback_query(call.id)

        session = get_session(user_id)

        if not session or not session.get("idea"):
            bot.send_message(
                chat_id,
                "❌ مفيش فكرة محفوظة.\n"
                "ابدأ مشروع جديد من القائمة.",
                reply_markup=main_menu(),
            )
            return

        session["step"] = "generating"

        generate_project_for_user(
            user_id=user_id,
            chat_id=chat_id,
            project_type=session["project_type"],
            idea=session["idea"],
        )

    # CANCEL PROJECT
    elif call.data == "cancel_project":
        bot.answer_callback_query(call.id)
        end_project(user_id)

        bot.send_message(
            chat_id,
            "❌ <b>تم إلغاء المشروع.</b>\n\n"
            "تقدر تبدأ مشروع جديد في أي وقت.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )

    # PROJECTS
    elif call.data == "projects":
        bot.answer_callback_query(call.id)

        projects = get_user_projects(user_id)

        if not projects:
            bot.send_message(
                chat_id,
                "📂 <b>مشاريعي</b>\n\n"
                "لسه معملتش أي مشاريع.",
                parse_mode="HTML",
            )
            return

        text = "📂 <b>مشاريعك</b>\n\n"

        for project in projects:
            project_id = project[0]
            project_type = project[1]
            project_name = project[2]
            created_at = project[4]

            icon = "🌐" if project_type == "website" else "🤖"

            text += (
                f"{icon} <b>{html.escape(str(project_name))}</b>\n"
                f"🆔 <code>{project_id}</code>\n"
                f"📅 {created_at}\n\n"
            )

        bot.send_message(chat_id, text, parse_mode="HTML")

    # STATS
    elif call.data == "stats":
        bot.answer_callback_query(call.id)

        projects = get_user_projects(user_id)
        website_count = 0
        bot_count = 0

        for project in projects:
            if project[1] == "website":
                website_count += 1
            elif project[1] == "telegram_bot":
                bot_count += 1

        bot.send_message(
            chat_id,
            "📊 <b>إحصائياتك</b>\n\n"
            f"📦 إجمالي المشاريع: <b>{len(projects)}</b>\n\n"
            f"🌐 المواقع: <b>{website_count}</b>\n"
            f"🤖 البوتات: <b>{bot_count}</b>",
            parse_mode="HTML",
        )

    # SETTINGS
    elif call.data == "settings":
        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            "⚙️ <b>إعدادات Code Generator</b>\n\n"
            "اختر الإعداد اللي عايز تعدله:",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=settings_menu(),
        )

    # HELP
    elif call.data == "help":
        bot.answer_callback_query(call.id)

        bot.send_message(
            chat_id,
            "📚 <b>مساعدة Code Generator</b>\n\n"
            "🌐 إنشاء موقع\n"
            "🤖 إنشاء Telegram Bot\n"
            "📸 رفع الصور والملفات\n"
            "📂 إدارة المشاريع\n"
            "📦 إنشاء ZIP\n\n"
            "❌ لإلغاء أي مشروع: اكتب /cancel",
            parse_mode="HTML",
        )

    # PROGRAMMING LANGUAGE
    elif call.data == "setting_programming":
        bot.answer_callback_query(call.id)

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                "🐍 Python", callback_data="lang_python"
            ),
            types.InlineKeyboardButton(
                "🌐 HTML/CSS/JS", callback_data="lang_web"
            ),
        )
        markup.add(
            types.InlineKeyboardButton(
                "🟨 JavaScript", callback_data="lang_js"
            ),
            types.InlineKeyboardButton(
                "🟦 TypeScript", callback_data="lang_ts"
            ),
        )
        markup.add(
            types.InlineKeyboardButton(
                "☕ Java", callback_data="lang_java"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "🔙 رجوع", callback_data="settings"
            )
        )

        bot.edit_message_text(
            "🌐 <b>لغة البرمجة</b>\n\n"
            "اختار اللغة المفضلة للمشاريع:",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=markup,
        )

    # CODE STYLE
    elif call.data == "setting_style":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "🎨 <b>شكل الأكواد</b>\n\n"
            "✨ Clean\n"
            "🏗️ Professional\n"
            "⚡ Performance\n\n"
            "🚧 هنربطها بالـAI Generator لاحقًا.",
            parse_mode="HTML",
        )

    # RESPONSE LANGUAGE
    elif call.data == "setting_language":
        bot.answer_callback_query(call.id)

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                "🇪🇬 العربية", callback_data="response_ar"
            ),
            types.InlineKeyboardButton(
                "🇬🇧 English", callback_data="response_en"
            ),
        )
        markup.add(
            types.InlineKeyboardButton(
                "🔄 تلقائي", callback_data="response_auto"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "🔙 رجوع", callback_data="settings"
            )
        )

        bot.edit_message_text(
            "📝 <b>لغة الردود</b>\n\n"
            "اختار لغة البوت:",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=markup,
        )

    # ZIP SETTINGS
    elif call.data == "setting_zip":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "📦 <b>إعدادات ZIP</b>\n\n"
            "☑️ README.md\n"
            "☑️ تنظيم الملفات\n"
            "☑️ مجلد assets\n"
            "☑️ مجلد images\n\n"
            "🚧 هنربطها بمولد المشاريع لاحقًا.",
            parse_mode="HTML",
        )

    # NOTIFICATIONS
    elif call.data == "setting_notifications":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "🔔 <b>الإشعارات</b>\n\n"
            "🟢 الإشعارات مفعلة.",
            parse_mode="HTML",
        )

    # DELETE DATA
    elif call.data == "delete_data":
        bot.answer_callback_query(call.id)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "❌ حذف البيانات",
                callback_data="confirm_delete",
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "🔙 إلغاء",
                callback_data="settings",
            )
        )

        bot.send_message(
            chat_id,
            "⚠️ <b>حذف البيانات</b>\n\n"
            "هل أنت متأكد؟",
            parse_mode="HTML",
            reply_markup=markup,
        )

    # CONFIRM DELETE
    elif call.data == "confirm_delete":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "🚧 نظام حذف البيانات الكامل "
            "هنفعله مع نظام الحسابات النهائي.",
            parse_mode="HTML",
        )

    # BACK TO MAIN
    elif call.data == "back_main":
        bot.answer_callback_query(call.id)

        bot.edit_message_text(
            f"🤖 <b>{BOT_NAME}</b>\n\n"
            "🚀 حوّل فكرتك إلى مشروع جاهز.\n\n"
            "اختار نوع المشروع اللي عايز تنشئه:",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=main_menu(),
        )

    # PROGRAMMING CHOICE
    elif call.data.startswith("lang_"):
        bot.answer_callback_query(call.id, "✅ تم حفظ الاختيار")
        bot.send_message(
            chat_id,
            "✅ تم حفظ لغة البرمجة.\n\n"
            "🚧 هنفعّل تأثيرها على المولّد لاحقًا.",
            parse_mode="HTML",
        )

    # RESPONSE LANGUAGE CHOICE
    elif call.data.startswith("response_"):
        bot.answer_callback_query(call.id, "✅ تم حفظ الاختيار")
        bot.send_message(
            chat_id,
            "✅ تم حفظ لغة الردود.",
            parse_mode="HTML",
        )


# ==========================================
# PHOTO HANDLER
# ==========================================

@bot.message_handler(content_types=["photo"])
def handle_photo(message):

    user_id = message.from_user.id
    session = get_session(user_id)

    if not session:
        bot.reply_to(
            message,
            "❌ مفيش مشروع شغال حاليًا.\n\n"
            "ابدأ مشروع جديد من القائمة.",
        )
        return

    if session["step"] != "images":
        bot.reply_to(
            message,
            "⚠️ مش بنستقبل صور في المرحلة دي.",
        )
        return

    bot.reply_to(
        message,
        "📸 استلمت الصورة ✅\n\n"
        "⏳ جاري تجهيزها داخل المشروع...",
    )

    try:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = file_info.file_path
        if "." in file_path:
            extension = "." + file_path.split(".")[-1]
        else:
            extension = ".jpg"

        image_number = len(session["images"]) + 1
        filename = f"image{image_number}{extension}"

        save_path = os.path.join(session["images_folder"], filename)

        with open(save_path, "wb") as image_file:
            image_file.write(downloaded_file)

        # Use session helper
        add_image(user_id, filename)

        bot.send_message(
            message.chat.id,
            f"✅ <b>تم حفظ الصورة!</b>\n\n"
            f"📸 {filename}\n"
            f"📁 <code>images/{filename}</code>\n\n"
            "ابعت صورة تانية أو اضغط «خلصت الصور».",
            parse_mode="HTML",
            reply_markup=finish_images_menu(),
        )

    except Exception as error:
        print("IMAGE ERROR:", error)
        bot.send_message(
            message.chat.id,
            "❌ حصل خطأ أثناء حفظ الصورة.\n\n"
            "جرب تبعتها تاني.",
        )


# ==========================================
# RUN
# ==========================================

print("========================================")
print(f"🤖 {BOT_NAME}")
print(f"📦 Version: {BOT_VERSION}")
print("💾 Database: Connected")
print("🧠 Generator: Connected")
print("👑 Admin notifications: ON")
print("📸 Image system: ON")
print("🚀 Bot is running...")
print("========================================")

bot.infinity_polling()
