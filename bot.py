from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from typing import Dict, List, Optional
import json
import random
from datetime import datetime
import asyncio

# 🔧 إعداد Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🎮 تخزين الألعاب والإحصائيات
games: Dict[int, Dict] = {}
stats: Dict[str, Dict] = {}
user_themes: Dict[int, str] = {}
game_timers: Dict[int, Dict] = {}

# 🎨 ثيمات متعددة
THEMES = {
    "classic": {"X": "❌", "O": "⭕", "empty": "⬜"},
    "hearts": {"X": "❤️", "O": "💙", "empty": "🤍"},
    "animals": {"X": "🐱", "O": "🐶", "empty": "⬜"},
    "fruits": {"X": "🍎", "O": "🍊", "empty": "⬜"},
    "space": {"X": "🌟", "O": "🌙", "empty": "⬛"},
    "emoji": {"X": "😎", "O": "🤓", "empty": "😶"}
}

# 🎵 ستيكرز للفوز والخسارة
STICKERS = {
    "win": [
        "CAACAgIAAxkBAAEMYP9nEqS9K8vWzAABXqYAAf8gAAFWYu8pAAJEAAPANk8Tyr8jhV9cAAEzHgQ",
        "CAACAgIAAxkBAAEMYQFnEqS-zQABvUBOj_b5q7Q-2z2JAAJEAAP7dGkW1Z_b5qg7zAABHgQ"
    ],
    "lose": [
        "CAACAgIAAxkBAAEMYQNnEqTBpCRGtKuJ1z5f2qAAAbq_UAACRAAD8SopFoq8AAFnq7zAAR4E",
        "CAACAgIAAxkBAAEMYQVnEqTCGQABPUqLtKr5fz_qAAG7U8UAAEQAA-8pKRaKvAABZ6u8wAEeBA"
    ],
    "draw": [
        "CAACAgIAAxkBAAEMYQdnEqTDvAABPq7Lt_r5fz_qAAG7U8UAAEQAA-8pKRaKvAABZ6u8wAEeBA"
    ]
}

# 💬 رسائل تشجيعية
MESSAGES = {
    "win": ["🎉 مبروك! أنت بطل!", "🏆 فوز رائع!", "⭐ أداء مميز!", "🔥 لاعب محترف!"],
    "lose": ["💪 حاول مرة أخرى!", "🎯 المرة القادمة أفضل!", "📚 تعلم من أخطائك!", "🌟 لا تستسلم!"],
    "draw": ["🤝 تعادل عادل!", "⚖️ مباراة متوازنة!", "🎲 كلاكما لعبتم بشكل جيد!"],
    "move": ["🎯 حركة ذكية!", "💡 فكر جيداً!", "⚡ وقتك يمر!", "🧠 استخدم عقلك!"]
}

# 📊 تحميل وحفظ البيانات
def load_data():
    """تحميل البيانات من الملف"""
    try:
        with open('xo_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"stats": {}, "themes": {}}

def save_data():
    """حفظ البيانات في الملف"""
    try:
        data = {"stats": stats, "themes": user_themes}
        with open('xo_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

# تحميل البيانات عند البدء
data = load_data()
stats = data.get("stats", {})
user_themes = {int(k): v for k, v in data.get("themes", {}).items()}

class XOGame:
    """فئة للتعامل مع منطق لعبة XO"""
    
    def __init__(self, user_id: int, timed_mode: bool = False):
        self.board: List[List[str]] = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player: str = "X"
        self.move_count: int = 0
        self.user_id = user_id
        self.timed_mode = timed_mode
        self.time_left = {"X": 60, "O": 60} if timed_mode else None
        self.last_move_time = datetime.now() if timed_mode else None
        self.theme = user_themes.get(user_id, "classic")
    
    def get_symbols(self):
        """الحصول على رموز الثيم الحالي"""
        return THEMES.get(self.theme, THEMES["classic"])
    
    def make_move(self, row: int, col: int) -> bool:
        """تنفيذ حركة اللاعب"""
        if self.board[row][col] == " ":
            # تحديث الوقت المتبقي
            if self.timed_mode and self.last_move_time:
                elapsed = (datetime.now() - self.last_move_time).total_seconds()
                self.time_left[self.current_player] -= elapsed
                if self.time_left[self.current_player] <= 0:
                    return False
            
            self.board[row][col] = self.current_player
            self.move_count += 1
            self.last_move_time = datetime.now() if self.timed_mode else None
            return True
        return False
    
    def check_winner(self) -> Optional[str]:
        """التحقق من الفائز"""
        # فحص الصفوف
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return self.board[i][0]
        
        # فحص الأعمدة
        for i in range(3):
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return self.board[0][i]
        
        # فحص الأقطار
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return self.board[1][1]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return self.board[1][1]
        
        return None
    
    def is_draw(self) -> bool:
        """التحقق من التعادل"""
        return self.move_count == 9 and self.check_winner() is None
    
    def check_timeout(self) -> Optional[str]:
        """التحقق من انتهاء الوقت"""
        if not self.timed_mode or not self.last_move_time:
            return None
        
        elapsed = (datetime.now() - self.last_move_time).total_seconds()
        if self.time_left[self.current_player] - elapsed <= 0:
            return self.current_player
        return None
    
    def switch_player(self):
        """تبديل اللاعب"""
        self.current_player = "O" if self.current_player == "X" else "X"
    
    def get_board_text(self) -> str:
        """الحصول على نص اللوحة"""
        symbols = self.get_symbols()
        lines = []
        for row in self.board:
            line = " │ ".join([symbols.get(cell, symbols["empty"]) for cell in row])
            lines.append(line)
        
        board_text = "\n" + "─" * 11 + "\n".join(["\n" + line + "\n" for line in lines]) + "─" * 11
        
        # إضافة معلومات الوقت
        if self.timed_mode:
            elapsed = (datetime.now() - self.last_move_time).total_seconds() if self.last_move_time else 0
            time_x = max(0, int(self.time_left["X"] - (elapsed if self.current_player == "X" else 0)))
            time_o = max(0, int(self.time_left["O"] - (elapsed if self.current_player == "O" else 0)))
            board_text += f"\n\n⏱️ الوقت: {symbols['X']} {time_x}s | {symbols['O']} {time_o}s"
        
        return board_text
    
    def get_keyboard(self) -> InlineKeyboardMarkup:
        """إنشاء لوحة المفاتيح"""
        symbols = self.get_symbols()
        keyboard = []
        for i in range(3):
            row = []
            for j in range(3):
                if self.board[i][j] == " ":
                    button_text = symbols["empty"]
                else:
                    button_text = symbols[self.board[i][j]]
                row.append(InlineKeyboardButton(button_text, callback_data=f"{i},{j}"))
            keyboard.append(row)
        
        # أزرار التحكم
        control_row = [
            InlineKeyboardButton("🔄 جديدة", callback_data="restart"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="show_stats"),
            InlineKeyboardButton("🎨 ثيم", callback_data="change_theme")
        ]
        keyboard.append(control_row)
        
        return InlineKeyboardMarkup(keyboard)

def get_user_stats(user_id: int) -> Dict:
    """الحصول على إحصائيات المستخدم"""
    user_id_str = str(user_id)
    if user_id_str not in stats:
        stats[user_id_str] = {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "total_games": 0,
            "history": []
        }
    return stats[user_id_str]

def update_stats(user_id: int, result: str):
    """تحديث الإحصائيات"""
    user_stats = get_user_stats(user_id)
    user_stats["total_games"] += 1
    
    if result == "win":
        user_stats["wins"] += 1
    elif result == "loss":
        user_stats["losses"] += 1
    elif result == "draw":
        user_stats["draws"] += 1
    
    # إضافة للتاريخ
    game_record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "result": result
    }
    user_stats["history"].insert(0, game_record)
    user_stats["history"] = user_stats["history"][:10]  # الاحتفاظ بآخر 10 فقط
    
    save_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة البداية"""
    keyboard = [
        [
            InlineKeyboardButton("🎮 لعب عادي", callback_data="mode_normal"),
            InlineKeyboardButton("⏱️ لعب بالوقت", callback_data="mode_timed")
        ],
        [
            InlineKeyboardButton("📊 إحصائياتي", callback_data="show_stats"),
            InlineKeyboardButton("🎨 تغيير الثيم", callback_data="change_theme")
        ],
        [
            InlineKeyboardButton("📜 تاريخ المباريات", callback_data="show_history"),
            InlineKeyboardButton("❓ مساعدة", callback_data="show_help")
        ]
    ]
    
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 أهلاً **{user_name}**!\n\n"
        "🎮 **مرحباً بك في لعبة XO المطورة!**\n\n"
        "اختر وضع اللعب للبدء:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة نقرات الأزرار"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    # اختيار الوضع العادي
    if query.data == "mode_normal":
        game = XOGame(user_id, timed_mode=False)
        games[chat_id] = game
        
        symbols = game.get_symbols()
        await query.edit_message_text(
            f"🎮 **لعبة جديدة!**\n\n"
            f"🎯 دور: {symbols['X']}\n"
            f"💡 {random.choice(MESSAGES['move'])}",
            reply_markup=game.get_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # اختيار الوضع بالوقت
    elif query.data == "mode_timed":
        game = XOGame(user_id, timed_mode=True)
        games[chat_id] = game
        
        symbols = game.get_symbols()
        await query.edit_message_text(
            f"⏱️ **وضع الوقت!**\n\n"
            f"⏰ لديك 60 ثانية لكل لاعب\n"
            f"🎯 دور: {symbols['X']}\n"
            f"💡 أسرع!",
            reply_markup=game.get_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    # تغيير الثيم
    elif query.data == "change_theme":
        keyboard = []
        for theme_name, theme_symbols in THEMES.items():
            emoji = "✅" if user_themes.get(user_id, "classic") == theme_name else ""
            button_text = f"{theme_symbols['X']} {theme_name.title()} {emoji}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"theme_{theme_name}")])
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")])
        
        await query.edit_message_text(
            "🎨 **اختر الثيم المفضل:**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # تطبيق الثيم
    elif query.data.startswith("theme_"):
        theme_name = query.data.replace("theme_", "")
        user_themes[user_id] = theme_name
        save_data()
        
        symbols = THEMES[theme_name]
        await query.answer(f"✅ تم تطبيق ثيم {theme_name}!", show_alert=True)
        await query.edit_message_text(
            f"✨ **تم تغيير الثيم!**\n\n"
            f"الثيم الجديد: {symbols['X']} {theme_name.title()}\n\n"
            f"جرب اللعب الآن!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🎮 ابدأ اللعب", callback_data="mode_normal"),
                InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")
            ]]),
            parse_mode='Markdown'
        )
        return
    
    # عرض الإحصائيات
    elif query.data == "show_stats":
        user_stats = get_user_stats(user_id)
        total = user_stats["total_games"]
        win_rate = (user_stats["wins"] / total * 100) if total > 0 else 0
        
        stats_text = (
            f"📊 **إحصائيات {user_name}**\n\n"
            f"🎮 المباريات: {total}\n"
            f"🏆 الانتصارات: {user_stats['wins']}\n"
            f"💔 الخسارات: {user_stats['losses']}\n"
            f"🤝 التعادل: {user_stats['draws']}\n"
            f"📈 نسبة الفوز: {win_rate:.1f}%\n"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]]
        await query.edit_message_text(
            stats_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # عرض التاريخ
    elif query.data == "show_history":
        user_stats = get_user_stats(user_id)
        history = user_stats.get("history", [])
        
        if not history:
            history_text = "📜 **لا توجد مباريات سابقة**\n\nابدأ اللعب لبناء تاريخك!"
        else:
            history_text = f"📜 **آخر {len(history)} مباريات:**\n\n"
            for i, game in enumerate(history, 1):
                result_emoji = {"win": "🏆", "loss": "💔", "draw": "🤝"}.get(game["result"], "🎮")
                history_text += f"{i}. {result_emoji} {game['result'].upper()} - {game['date']}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]]
        await query.edit_message_text(
            history_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # المساعدة
    elif query.data == "show_help":
        help_text = (
            "📖 **دليل اللعبة:**\n\n"
            "🎮 **الأوضاع:**\n"
            "• عادي: لعب بدون حدود زمنية\n"
            "• بالوقت: 60 ثانية لكل لاعب\n\n"
            "🎨 **الثيمات:**\n"
            "• 6 ثيمات مختلفة للاختيار\n"
            "• غير الثيم من الإعدادات\n\n"
            "📊 **الإحصائيات:**\n"
            "• تُحفظ كل نتائجك تلقائياً\n"
            "• شاهد آخر 10 مباريات\n\n"
            "🎵 **المكافآت:**\n"
            "• ستيكرز عند الفوز/الخسارة\n"
            "• رسائل تشجيعية مستمرة\n\n"
            "💡 **نصيحة:** العب باستمرار لتحسين إحصائياتك!"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]]
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # رجوع للقائمة
    elif query.data == "back_to_menu":
        keyboard = [
            [
                InlineKeyboardButton("🎮 لعب عادي", callback_data="mode_normal"),
                InlineKeyboardButton("⏱️ لعب بالوقت", callback_data="mode_timed")
            ],
            [
                InlineKeyboardButton("📊 إحصائياتي", callback_data="show_stats"),
                InlineKeyboardButton("🎨 تغيير الثيم", callback_data="change_theme")
            ],
            [
                InlineKeyboardButton("📜 تاريخ المباريات", callback_data="show_history"),
                InlineKeyboardButton("❓ مساعدة", callback_data="show_help")
            ]
        ]
        
        await query.edit_message_text(
            f"👋 أهلاً **{user_name}**!\n\n🎮 اختر وضع اللعب:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    game = games.get(chat_id)
    
    if not game:
        await query.answer("❌ اللعبة غير موجودة!", show_alert=True)
        return
    
    # إعادة اللعب
    if query.data == "restart":
        keyboard = [
            [
                InlineKeyboardButton("🎮 عادي", callback_data="mode_normal"),
                InlineKeyboardButton("⏱️ بالوقت", callback_data="mode_timed")
            ],
            [InlineKeyboardButton("🔙 القائمة", callback_data="back_to_menu")]
        ]
        await query.edit_message_text(
            "🔄 **لعبة جديدة؟**\n\nاختر الوضع:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        if chat_id in games:
            del games[chat_id]
        return
    
    # التحقق من انتهاء الوقت
    timeout_player = game.check_timeout()
    if timeout_player:
        winner = "O" if timeout_player == "X" else "X"
        update_stats(user_id, "loss")
        
        symbols = game.get_symbols()
        result_text = (
            f"⏰ **انتهى الوقت!**\n\n"
            f"💔 {random.choice(MESSAGES['lose'])}\n"
            f"🏆 الفائز: {symbols[winner]}\n\n"
            f"{game.get_board_text()}"
        )
        
        keyboard = [[
            InlineKeyboardButton("🔄 لعب مرة أخرى", callback_data="restart"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="show_stats")
        ]]
        
        await query.edit_message_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # إرسال ستيكر
        try:
            sticker_id = random.choice(STICKERS["lose"])
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
        except:
            pass
        
        return
    
    # تنفيذ الحركة
    try:
        row, col = map(int, query.data.split(","))
    except ValueError:
        return
    
    if not game.make_move(row, col):
        await query.answer("⚠️ المربع محجوز أو انتهى وقتك!", show_alert=True)
        return
    
    symbols = game.get_symbols()
    
    # التحقق من الفائز
    winner = game.check_winner()
    if winner:
        if winner == "X":
            update_stats(user_id, "win")
            result_msg = f"🎉 {random.choice(MESSAGES['win'])}"
            sticker_type = "win"
        else:
            update_stats(user_id, "loss")
            result_msg = f"😔 {random.choice(MESSAGES['lose'])}"
            sticker_type = "lose"
        
        result_text = (
            f"{result_msg}\n\n"
            f"🏆 الفائز: {symbols[winner]}\n"
            f"{game.get_board_text()}\n\n"
            f"📊 الحركات: {game.move_count}"
        )
        
        keyboard = [[
            InlineKeyboardButton("🔄 لعب مرة أخرى", callback_data="restart"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="show_stats")
        ]]
        
        await query.edit_message_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # إرسال ستيكر
        try:
            sticker_id = random.choice(STICKERS[sticker_type])
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
        except:
            pass
        
        return
    
    # التحقق من التعادل
    if game.is_draw():
        update_stats(user_id, "draw")
        result_text = (
            f"🤝 {random.choice(MESSAGES['draw'])}\n\n"
            f"{game.get_board_text()}\n\n"
            f"📊 الحركات: {game.move_count}"
        )
        
        keyboard = [[
            InlineKeyboardButton("🔄 لعب مرة أخرى", callback_data="restart"),
            InlineKeyboardButton("📊 إحصائيات", callback_data="show_stats")
        ]]
        
        await query.edit_message_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # إرسال ستيكر
        try:
            sticker_id = random.choice(STICKERS["draw"])
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
        except:
            pass
        
        return
    
    # تبديل اللاعب ومتابعة اللعب
    game.switch_player()
    encouragement = random.choice(MESSAGES['move'])
    
    await query.edit_message_text(
        f"🎯 **دور:** {symbols[game.current_player]}\n"
        f"💡 {encouragement}\n"
        f"{game.get_board_text()}",
        reply_markup=game.get_keyboard(),
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """تشغيل البوت"""
    TOKEN = "8115080119:AAFyvt43RPPZ8irKirKL46XxBQrPUoH7QKE"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running with new features!")
    print("✅ Bot is running!")
    print("🎨 Themes: 6 available")
    print("⏱️ Timed mode: Enabled")
    print("📊 Stats & History: Enabled")
    print("🎵 Stickers: Enabled")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()