import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters, ConversationHandler
)
from database import (
    init_db, get_user_prayers, update_prayer, get_total_missed,
    is_setup_completed, save_initial_prayers, get_history, reset_user_setup
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Conversation states
SETUP_BOMDOD, SETUP_PESHIN, SETUP_ASR, SETUP_SHOM, SETUP_XUFTON, SETUP_VITR, CONFIRM_SETUP = range(7)
SELECT_PRAYER_ADD, ENTER_AMOUNT_ADD = range(7, 9)
SELECT_PRAYER_SUB, ENTER_AMOUNT_SUB = range(9, 11)

# Prayer names in Uzbek
PRAYER_NAMES = {
    'bomdod': '🌅 Bomdod',
    'peshin': '☀️ Peshin',
    'asr': '🌤️ Asr',
    'shom': '🌆 Shom',
    'xufton': '🌙 Xufton',
    'vitr': '✨ Vitr'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    
    if is_setup_completed(user_id):
        await update.message.reply_text(
            "Assalamu Alaikum! 🕌\n\n"
            "Botdan foydalanish:\n\n"
            "📊 /status - Joriy qoldiq namozlar\n"
            "➕ /add - Qoldiq namoz qo'shish\n"
            "➖ /subtract - Qoldiq namozni ayirish\n"
            "📜 /history - Oxirgi o'zgarishlar\n"
            "🔄 /reset - Qaytadan boshidan sozlash\n"
            "❓ /help - Yordam"
        )
        return ConversationHandler.END  # ADD THIS LINE
    else:
        await update.message.reply_text(
            "Assalamu Alaikum! 🕌\n\n"
            "Iltimos, qoldiq namozlaringiz sonini kiriting.\n\n"
            "Birinchi navbatda Bomdod namozi qoldiq sonini kiriting:"
        )
        return SETUP_BOMDOD
    """Start command handler"""
    user_id = update.effective_user.id
    
    if is_setup_completed(user_id):
        await update.message.reply_text(
            "Assalamu Alaikum! 🕌\n\n"
            "Botdan foydalanish:\n\n"
            "📊 /status - Joriy qoldiq namozlar\n"
            "➕ /add - Qoldiq namoz qo'shish\n"
            "➖ /subtract - Qoldiq namozni ayirish\n"
            "📜 /history - Oxirgi o'zgarishlar\n"
            "🔄 /reset - Qaytadan boshidan sozlash\n"
            "❓ /help - Yordam"
        )
    else:
        await update.message.reply_text(
            "Assalamu Alaikum! 🕌\n\n"
            "Iltimos, qoldiq namozlaringiz sonini kiriting.\n\n"
            "Birinchi navbatda Bomdod namozi qoldiq sonini kiriting:"
        )
        return SETUP_BOMDOD

async def setup_bomdod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Bomdod count"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_BOMDOD
        
        context.user_data['bomdod'] = count
        await update.message.reply_text("Peshin namozi qoldiq sonini kiriting:")
        return SETUP_PESHIN
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_BOMDOD

async def setup_peshin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Peshin count"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_PESHIN
        
        context.user_data['peshin'] = count
        await update.message.reply_text("Asr namozi qoldiq sonini kiriting:")
        return SETUP_ASR
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_PESHIN

async def setup_asr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Asr count"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_ASR
        
        context.user_data['asr'] = count
        await update.message.reply_text("Shom namozi qoldiq sonini kiriting:")
        return SETUP_SHOM
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_ASR

async def setup_shom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Shom count"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_SHOM
        
        context.user_data['shom'] = count
        await update.message.reply_text("Xufton namozi qoldiq sonini kiriting:")
        return SETUP_XUFTON
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_SHOM

async def setup_xufton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Xufton count"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_XUFTON
        
        context.user_data['xufton'] = count
        await update.message.reply_text("Vitr namozi qoldiq sonini kiriting:")
        return SETUP_VITR
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_XUFTON

async def setup_vitr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get Vitr count and show confirmation"""
    try:
        count = int(update.message.text)
        if count < 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return SETUP_VITR
        
        context.user_data['vitr'] = count
        
        # Show summary for confirmation
        summary = "📋 Kiritilgan ma'lumotlar:\n\n"
        summary += f"🌅 Bomdod: {context.user_data['bomdod']}\n"
        summary += f"☀️ Peshin: {context.user_data['peshin']}\n"
        summary += f"🌤️ Asr: {context.user_data['asr']}\n"
        summary += f"🌆 Shom: {context.user_data['shom']}\n"
        summary += f"🌙 Xufton: {context.user_data['xufton']}\n"
        summary += f"✨ Vitr: {context.user_data['vitr']}\n\n"
        
        total = sum(context.user_data.values())
        summary += f"📊 Jami: {total} namoz\n\n"
        summary += "To'g'rimi?"
        
        keyboard = [
            [InlineKeyboardButton("✅ Ha, saqlash", callback_data='confirm_yes')],
            [InlineKeyboardButton("✏️ Yo'q, qaytadan kiritish", callback_data='confirm_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, reply_markup=reply_markup)
        return CONFIRM_SETUP
        
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return SETUP_VITR

async def confirm_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation of initial setup"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_yes':
        user_id = update.effective_user.id
        prayers = {
            'bomdod': context.user_data['bomdod'],
            'peshin': context.user_data['peshin'],
            'asr': context.user_data['asr'],
            'shom': context.user_data['shom'],
            'xufton': context.user_data['xufton'],
            'vitr': context.user_data['vitr']
        }
        
        save_initial_prayers(user_id, prayers)
        
        await query.edit_message_text(
            "✅ Ma'lumotlar saqlandi!\n\n"
            "Buyruqlar:\n"
            "📊 /status - Joriy qoldiq\n"
            "➕ /add - Namoz qo'shish\n"
            "➖ /subtract - Namoz ayirish\n"
            "📜 /history - Tarix"
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await query.edit_message_text(
            "Qaytadan boshlash uchun /start yozing."
        )
        context.user_data.clear()
        return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current missed prayers"""
    user_id = update.effective_user.id
    
    if not is_setup_completed(user_id):
        await update.message.reply_text(
            "Iltimos, avval /start buyrug'i orqali ma'lumotlarni kiriting."
        )
        return
    
    prayers = get_user_prayers(user_id)
    total = get_total_missed(user_id)
    
    message = "📊 Qoldiq Namozlar:\n\n"
    for key, name in PRAYER_NAMES.items():
        message += f"{name}: {prayers[key]}\n"
    message += f"\n📈 Jami: {total} namoz"
    
    await update.message.reply_text(message)

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding prayers"""
    user_id = update.effective_user.id
    
    if not is_setup_completed(user_id):
        await update.message.reply_text(
            "Iltimos, avval /start buyrug'i orqali ma'lumotlarni kiriting."
        )
        return ConversationHandler.END
    
    keyboard = []
    for key, name in PRAYER_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f'add_{key}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Qaysi namozni qo\'shmoqchisiz?', reply_markup=reply_markup)
    return SELECT_PRAYER_ADD

async def add_select_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prayer selection for adding"""
    query = update.callback_query
    await query.answer()
    
    prayer = query.data.replace('add_', '')
    context.user_data['selected_prayer'] = prayer
    
    await query.edit_message_text(
        f"{PRAYER_NAMES[prayer]} namozi uchun nechta qo'shmoqchisiz?\n"
        "Raqam kiriting:"
    )
    return ENTER_AMOUNT_ADD

async def add_enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle amount entry for adding"""
    try:
        amount = int(update.message.text)
        if amount <= 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return ENTER_AMOUNT_ADD
        
        user_id = update.effective_user.id
        prayer = context.user_data['selected_prayer']
        
        update_prayer(user_id, prayer, amount, 'added')
        
        await update.message.reply_text(
            f"✅ {PRAYER_NAMES[prayer]} ga {amount} ta qo'shildi!\n\n"
            f"Joriy holat ko'rish: /status"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return ENTER_AMOUNT_ADD

async def subtract_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start subtracting prayers"""
    user_id = update.effective_user.id
    
    if not is_setup_completed(user_id):
        await update.message.reply_text(
            "Iltimos, avval /start buyrug'i orqali ma'lumotlarni kiriting."
        )
        return ConversationHandler.END
    
    keyboard = []
    for key, name in PRAYER_NAMES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f'sub_{key}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Qaysi namozni ayirmoqchisiz?', reply_markup=reply_markup)
    return SELECT_PRAYER_SUB

async def subtract_select_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prayer selection for subtracting"""
    query = update.callback_query
    await query.answer()
    
    prayer = query.data.replace('sub_', '')
    context.user_data['selected_prayer'] = prayer
    
    prayers = get_user_prayers(update.effective_user.id)
    current = prayers[prayer]
    
    await query.edit_message_text(
        f"{PRAYER_NAMES[prayer]} - Joriy qoldiq: {current}\n\n"
        f"Nechta ayirmoqchisiz?\n"
        "Raqam kiriting:"
    )
    return ENTER_AMOUNT_SUB

async def subtract_enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle amount entry for subtracting"""
    try:
        amount = int(update.message.text)
        if amount <= 0:
            await update.message.reply_text("Iltimos, musbat son kiriting:")
            return ENTER_AMOUNT_SUB
        
        user_id = update.effective_user.id
        prayer = context.user_data['selected_prayer']
        prayers = get_user_prayers(user_id)
        
        if prayers[prayer] < amount:
            await update.message.reply_text(
                f"⚠️ Sizda {PRAYER_NAMES[prayer]} dan faqat {prayers[prayer]} ta bor.\n"
                f"Boshqa son kiriting yoki /cancel"
            )
            return ENTER_AMOUNT_SUB
        
        update_prayer(user_id, prayer, -amount, 'completed')
        
        await update.message.reply_text(
            f"✅ {PRAYER_NAMES[prayer]} dan {amount} ta ayrildi!\n\n"
            f"Joriy holat ko'rish: /status"
        )
        
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("Iltimos, faqat raqam kiriting:")
        return ENTER_AMOUNT_SUB

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show prayer history"""
    user_id = update.effective_user.id
    
    if not is_setup_completed(user_id):
        await update.message.reply_text(
            "Iltimos, avval /start buyrug'i orqali ma'lumotlarni kiriting."
        )
        return
    
    history = get_history(user_id, 15)
    
    if not history:
        await update.message.reply_text("📜 Hali tarix yo'q.")
        return
    
    message = "📜 Oxirgi o'zgarishlar:\n\n"
    
    action_emoji = {
        'added': '➕',
        'completed': '✅',
        'initial_setup': '📝'
    }
    
    # Reverse the history to show oldest first, newest last
    for prayer_name, action, amount, timestamp in reversed(history):
        emoji = action_emoji.get(action, '📌')
        action_text = {
            'added': 'qo\'shildi',
            'completed': 'o\'qildi',  # Changed from 'qilindi' to 'o'qildi'
            'initial_setup': 'boshlang\'ich'
        }.get(action, action)
        
        message += f"{emoji} {PRAYER_NAMES[prayer_name]}: {amount} ({action_text})\n"
        message += f"⏰ {timestamp}\n\n"
    
    await update.message.reply_text(message)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user setup"""
    user_id = update.effective_user.id
    reset_user_setup(user_id)
    
    await update.message.reply_text(
        "🔄 Ma'lumotlar tozalandi.\n\n"
        "Qaytadan boshlash uchun /start yozing."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text("❌ Bekor qilindi.")
    context.user_data.clear()
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        "🕌 Namoz Tracker Bot\n\n"
        "Buyruqlar:\n"
        "📊 /status - Joriy qoldiq namozlar\n"
        "➕ /add - Qoldiq namoz qo'shish\n"
        "➖ /subtract - O'qilgan namozni ayirish\n"
        "📜 /history - Oxirgi o'zgarishlar tarixi\n"
        "🔄 /reset - Ma'lumotlarni qaytadan kiritish\n"
        "❓ /help - Yordam\n\n"
        "Savollar bo'lsa @abu_muhammad_umar ga murojaat qiling."
    )

def main():
    """Start the bot"""
    # Initialize database
    init_db()

    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Conversation handler for setup
    setup_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SETUP_BOMDOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_bomdod)],
            SETUP_PESHIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_peshin)],
            SETUP_ASR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_asr)],
            SETUP_SHOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_shom)],
            SETUP_XUFTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_xufton)],
            SETUP_VITR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_vitr)],
            CONFIRM_SETUP: [CallbackQueryHandler(confirm_setup)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Conversation handler for adding prayers
    add_conv = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            SELECT_PRAYER_ADD: [CallbackQueryHandler(add_select_prayer)],
            ENTER_AMOUNT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Conversation handler for subtracting prayers
    subtract_conv = ConversationHandler(
        entry_points=[CommandHandler('subtract', subtract_start)],
        states={
            SELECT_PRAYER_SUB: [CallbackQueryHandler(subtract_select_prayer)],
            ENTER_AMOUNT_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, subtract_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add all handlers to the application
    application.add_handler(setup_conv)
    application.add_handler(add_conv)
    application.add_handler(subtract_conv)
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    print("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()
    """Start the bot"""
    # Initialize database
    init_db()

    # Create the bot application
    application = Application.builder().token(TOKEN).build()

    # Conversation handler for setup
    setup_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SETUP_BOMDOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_bomdod)],
            SETUP_PESHIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_peshin)],
            SETUP_ASR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_asr)],
            SETUP_SHOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_shom)],
            SETUP_XUFTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_xufton)],
            SETUP_VITR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_vitr)],
            CONFIRM_SETUP: [CallbackQueryHandler(confirm_setup)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Conversation handler for adding prayers
    add_conv = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            SELECT_PRAYER_ADD: [CallbackQueryHandler(add_select_prayer)],
            ENTER_AMOUNT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Conversation handler for subtracting prayers
    subtract_conv = ConversationHandler(
        entry_points=[CommandHandler('subtract', subtract_start)],
        states={
            SELECT_PRAYER_SUB: [CallbackQueryHandler(subtract_select_prayer)],
            ENTER_AMOUNT_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, subtract_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add all handlers to the application
    application.add_handler(setup_conv)
    application.add_handler(add_conv)
    application.add_handler(subtract_conv)
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    print("Bot is running...")
    application.run_polling()

    """Start the bot"""
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Setup conversation handler
    setup_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SETUP_BOMDOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_bomdod)],
            SETUP_PESHIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_peshin)],
            SETUP_ASR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_asr)],
            SETUP_SHOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_shom)],
            SETUP_XUFTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_xufton)],
            SETUP_VITR: [MessageHandler(filters.TEXT & ~filters.COMMAND, setup_vitr)],
            CONFIRM_SETUP: [CallbackQueryHandler(confirm_setup)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add conversation handler
    add_conv = ConversationHandler(
        entry_points=[CommandHandler('add', add_start)],
        states={
            SELECT_PRAYER_ADD: [CallbackQueryHandler(add_select_prayer)],
            ENTER_AMOUNT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Subtract conversation handler
    subtract_conv = ConversationHandler(
        entry_points=[CommandHandler('subtract', subtract_start)],
        states={
            SELECT_PRAYER_SUB: [CallbackQueryHandler(subtract_select_prayer)],
            ENTER_AMOUNT_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, subtract_enter_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add all handlers
    application.add_handler(setup_conv)
    application.add_handler(add_conv)
    application.add_handler(subtract_conv)
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start bot
    print("Bot is running...")
    application = Application.builder().token(TOKEN).build()


if __name__ == '__main__':
    main()