import os, json, random, asyncio, time, logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, AIORateLimiter
from telegram.error import RetryAfter, TimedOut, NetworkError

# ВАЖНО: ТВОЙ ТОКЕН (лучше вынести в переменную окружения позже)
TOKEN = "8384986879:AAGUBtm3Fg0cNUa-IlroraoWQ1M7eMz2PNM"

# Логирование
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)

# Погоняла (слиты в один список, без вложенного "nicknames = [...]")
NICKNAMES = [
    "Лепман Коричневый Змей", "Лепман Марафон Коричневых Змей", "Лепман Снюсный Барон", "Лепман Король Желтых Дождей",
    "Лепман Линьчиковый Лежун", "Лепман Животик+2кг", "Лепман Балду Пинатель", "Лепман Унитаз — Это Жизнь",
    "Лепман Железный Снюсоносец", "Лепман Титан Подоконника", "Лепман Властелин Люкса", "Лепман Папа Линьчика",
    "Лепман Гроза Окон", "Лепман Шлёп Утренний", "Лепман Книга-Моча", "Лепман Лежит И Красивый",
    "Лепман 110 Коричневый", "Лепман С Продристью", "Лепман Вечный Балабол", "Лепман Круг Самопотерянных",
    "Верховный Бушист",
    "Главный Анус", "Кикша-Пожиратель", "Бушистый Подзалупин", "Анусоносец", "Кикша Линьчиковая",
    "Повелитель Бушизма и Анусов", "Сипарь С Очком", "Гнойный Линьчикарь", "Магистр Заднепрохода",
    "Трипперный Бушонок", "Кикша-Пердуша", "Анусоразрушитель", "Сипун Глубокого Очка", "Кикшевый Громила",
    "Очконосный Архонт", "Анусоед Линьчиков", "Бушизмовод Очковый", "Кикша-Вонючка", "Сипоносец Анусов",
    "Паховый Линьчикарь", "Заднепроходный Пророк", "Кикша Мясная", "Линьчикоанус", "Очковый Шаман",
    "Кикша-Разрушитель", "Анусный Оракул", "Бушист Сраный", "Гнойно-Сипучий", "Кикша-Вертолёт",
    "Очкодав Бушизма", "Сральный Линьчикарь", "Кикшевый Сосальщик", "Анусообниматель", "Линьчикоразрыватель",
    "Сипарь Очковый", "Кикша-Мочалка", "Бушизмовый Говнарь", "Очковый Кикшевод", "Анусоносный Линьчикарь",
    "Кикша Сырная", "Очкосос Легендарный", "Линьчикоочкоед", "Кикша-Свинтус", "Очкодавец Бушистый",
    "Анусовый Гроза", "Кикша Плесневелая", "Сипарь Глубинный", "Очкоразрушитель Линьчиков", "Кикша Кислотная",
    "Бушизмопердун", "Очковый Повелитель", "Кикша-Венеричка", "Линьчикоочковый", "Гнойно-Кикшевый",
    "Анусоноситель", "Кикша-Хрюша", "Очковый Линьчикарь", "Сипарь Анусный", "Кикша-Жмур", "Очкозавр",
    "Анусораздуватель", "Линьчикоанальный", "Кикша-Брызгун", "Очковый Рыцарь", "Гнойный Очкоед",
    "Кикша-Мазохист", "Анусоочиститель", "Очкокидатель", "Кикша-Червивый", "Бушизмосраколиз",
    "Очковый Инквизитор", "Кикша-Перделка", "Анусотряс", "Сипарь Сральный", "Очкосекущий",
    "Кикша-Заднеприводный", "Линьчикосос Анусов", "Очконосец", "Кикша-Вшивка", "Анусобушонок",
    "Очковый Зверь", "Кикша-Срачмейстер", "Гнойно-Анусный", "Очкотрон 3000", "Кикша-Бушист",
    "Анусодушитель", "Очковый Мрак", "Кикша-Пердач", "Анусорез", "Очковый Линьчикоед", "Кикша-Сипарь",
    "Бушизмочкоед", "Очковый Вонючка", "Кикша-Анусонос", "Сипарь Очковый Грозный", "Попочка с сисечками",
    "Анусоразбойник", "Кикша-Очковерт", "Очковый Линьчикоразрушитель",
    "Лепман Мастер Проливных Дождей", "Лепман Линьчиковый Гладиатор", "Лепман Снюс на Вечер",
    "Лепман Хранитель Преворкаута", "Лепман Писатель Битов", "Лепман Писаться Идём", "Лепман Сношающий Рты",
    "Лепман Легенда Жёлтого Потока", "Лепман Я Реально Красивый", "Лепман Властелин Линьчика", "Лепман Мастер 30 Секунд",
    "Лепман Философ Унитаза", "Лепман Проклятый Линьчикер", "Лепман Шаман Желтых Дождей", "Лепман Снюсный Унитазист",
    "Лепман Разгон До 110", "Лепман Человек-Снюс", "Лепман Битмейкер Линьчика", "Лепман Преворкаутный",
    "Лепман Снюсо-Варвар", "Лепман Гроза Книг-Мочи", "Лепман Железный Преворкаут", "Лепман Жёлтый Поток",
    "Лепман Мочевой Магистр", "Лепман Властелин Балды", "Лепман Линьчиковый Мститель", "Лепман Легенда Снюса",
    "Лепман Книга-Снюс", "Лепман Мастер Бутылочного Дождя", "Лепман Король Продристи", "Лепман Снюсо-Рокер",
    "Лепман Мокрый Линьчик", "Лепман Железный Лежун", "Лепман Преворкаутный Шаман", "Лепман Снюсо-Босс",
    "Лепман Книга-Гроза", "Лепман Жёлтый Призыватель", "Лепман Линьчиковый Принц", "Лепман Гроза Люкса",
    "Лепман Марафонщик Линьчика", "Лепман Папа Продристи", "Лепман Легенда Марафона", "Лепман Железный Снюс-Маг",
    "Лепман Король Оконных Дождей", "Лепман Мастер Потоков", "Лепман Балду-Каратель", "Лепман Снюсный Философ",
    "Лепман Преворкаутный Барон", "Лепман Линьчиковый Разрушитель", "Лепман Гроза Сантехники", "Лепман Жёлтый Маг",
    "Лепман Властелин Продристь", "Лепман Марафон Люксов", "Лепман Железный Балабол", "Лепман Снюсный Бродяга",
    "Лепман Преворкаутный Гладиатор", "Лепман Линьчиковый Певец", "Лепман Мастер Жёлтого Потока", "Лепман Книга-Воин",
    "Лепман Снюсо-Легенда", "Лепман Железный Поточник", "Лепман Гроза 110", "Лепман Марафон Мочи",
    "Лепман Властелин Линьчиковых Ночей", "Лепман Мастер Продристь", "Лепман Снюсный Принц", "Лепман Балду-Ломатель",
    "Лепман Железный Книгач", "Лепман Линьчиковый Шутник", "Лепман Преворкаутный Лев", "Лепман Жёлтый Джедай",
    "Лепман Книга-Гладиатор", "Лепман Снюсо-Герой", "Лепман Мастер Люксов", "Лепман Гроза Линьчика",
    "Лепман Железный Дождевик", "Лепман Преворкаутный Сокол", "Лепман Линьчиковый Левиафан", "Лепман Снюсный Рыцарь",
    "Лепман Легенда Книг", "Лепман Железный Мочевик", "Лепман Преворкаутный Чародей", "Лепман Марафонский Жрец",
    "Лепман Балду-Разрушитель", "Лепман Линьчиковый Орёл", "Лепман Жёлтый Фараон", "Лепман Снюсный Гуру",
    "Лепман Книга-Царь", "Лепман Преворкаутный Волк", "Лепман Железный Шаман", "Лепман Гроза Потоков",
    "Лепман Марафон Линьчика", "Лепман Линьчиковый Шаман", "Лепман Снюсо-Мастер", "Лепман Книга-Властелин",
    "Лепман Жёлтый Гладиатор", "Лепман Преворкаутный Легенд", "Лепман Железный Линьчикер", "Лепман Балду-Монарх",
    "Лепман Линьчиковый Властелин", "Лепман Снюсный Лев", "Лепман Марафонный Джин", "Лепман Жёлтый Босс",
    "Лепман Преворкаутный Папа", "Лепман Книга-Балабол", "Лепман Железный Люкс", "Лепман Снюсо-Бог",
    "Лепман Гроза Марафона", "Лепман Линьчиковый Папа", "Лепман Марафонщик Люксов", "Лепман Жёлтый Гроза",
    "Лепман Балду-Легенда", "Лепман Преворкаутный Орёл", "Лепман Книга-Поток", "Лепман Железный Марафонец",
    "Лепман Снюсо-Властелин", "Лепман Линьчиковый Волк", "Лепман Жёлтый Шаман", "Лепман Балду-Магистр",
    "Лепман Преворкаутный Гроза", "Лепман Книга-Дождевик", "Лепман Железный Поток", "Лепман Снюсо-Орёл",
    "Лепман Линьчиковый Барон", "Лепман Марафонский Волк", "Лепман Жёлтый Легенд", "Лепман Балду-Папа",
    "Лепман Преворкаутный Мастер", "Лепман Книга-Орёл", "Лепман Железный Властелин", "Лепман Снюсо-Джедай",
    "Лепман Линьчиковый Джин", "Лепман Марафонский Лев", "Лепман Жёлтый Призрак", "Лепман Балду-Герой",
    "Лепман Преворкаутный Линьчикер", "Лепман Книга-Гроза", "Лепман Железный Лев", "Лепман Снюсо-Фараон",
    "Лепман Линьчиковый Бог", "Лепман Марафонский Линьчик", "Лепман Жёлтый Книгач", "Лепман Балду-Мочевик",
    "Лепман Преворкаутный Поток", "Лепман Книга-Марафонец", "Лепман Сип-мастер", "Лепман Великий Сипун",
    "Лепман Сип-Барон", "Лепман Легенда Сипа", "Лепман Король Сипа", "Лепман Сипун Гладиатор",
    "Лепман Сип-Гроза", "Лепман Сипун Шаман", "Лепман Сипный Волк", "Лепман Марафон Сипа"
]

# можно фильтровать слова, которые не хочешь выпускать
BANNED_SUBSTRINGS = {"даун"}
NICKNAMES = [n for n in NICKNAMES if all(b.lower() not in n.lower() for b in BANNED_SUBSTRINGS)]

BTN_GEN = "Сгенерировать погоняло"
BTN_POST = "Отправить в канал"
STORE_FILE = "channel_binding.json"

_last_call = {}
def _cooldown(chat_id: int, cooldown=1.0) -> bool:
    now = time.monotonic()
    prev = _last_call.get(chat_id, 0)
    if now - prev < cooldown:
        return False
    _last_call[chat_id] = now
    return True

def make_markup():
    return ReplyKeyboardMarkup([[BTN_GEN, BTN_POST]], resize_keyboard=True)

def pick_name_html() -> str:
    nickname = random.choice(NICKNAMES)
    core = nickname.replace("Лепман", "").strip(" —-")
    return f"<b>Лепман</b> — <i>{core}</i>"

def load_binding():
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_binding(data):
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "тыкни кнопку, чтобы выдать рофельное прозвище (•‿•)", reply_markup=make_markup()
    )

async def nickname_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _cooldown(update.effective_chat.id):
        return
    await update.effective_message.reply_html(pick_name_html())

async def lep_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _cooldown(update.effective_chat.id):
        return
    msg = update.effective_message
    try:
        await msg.reply_html(pick_name_html())
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 0.2)
        await msg.reply_html(pick_name_html())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.effective_message.text or "").strip()
    if txt == BTN_GEN:
        if _cooldown(update.effective_chat.id):
            await update.effective_message.reply_html(pick_name_html())
    elif txt == BTN_POST:
        bind = load_binding()
        target = bind.get("chat_identifier")
        if not target:
            return await update.effective_message.reply_text(
                "Канал не привязан. Используй /bind_channel @username или перешли мне пост из канала (для приватного)."
            )
        await context.bot.send_message(chat_id=target, text=pick_name_html(), parse_mode="HTML")
        await update.effective_message.reply_text("Отправил в канал ✔️")
    else:
        await update.effective_message.reply_text("жми кнопку ниже ↓", reply_markup=make_markup())

async def bind_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.effective_message.reply_text("Использование: /bind_channel @username_канала")
    username = context.args[0]
    if not username.startswith("@"):
        return await update.effective_message.reply_text("Укажи канал с @, например: /bind_channel @my_channel")
    chat = await context.bot.get_chat(username)
    save_binding({"chat_identifier": username, "chat_title": chat.title or username, "chat_id": chat.id})
    await update.effective_message.reply_text(f"Привязал канал: {chat.title} (идентификатор {username})")

async def bind_by_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg and msg.forward_from_chat and msg.forward_from_chat.type == "channel":
        ch = msg.forward_from_chat
        save_binding({"chat_identifier": ch.id, "chat_title": ch.title or str(ch.id), "chat_id": ch.id})
        await update.effective_message.reply_text(f"Привязал приватный канал: {ch.title} (ID {ch.id}) ✅")

async def post_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bind = load_binding()
    target = bind.get("chat_identifier")
    if not target:
        return await update.effective_message.reply_text("Сначала привяжи канал: /bind_channel @username или пришли форвард из канала.")
    await context.bot.send_message(chat_id=target, text=pick_name_html(), parse_mode="HTML")
    await update.effective_message.reply_text("Отправил в канал ✔️")

async def error_handler(update: object, context):
    ex = context.error
    logging.warning(f"Error: {ex}")
    if isinstance(ex, RetryAfter):
        await asyncio.sleep(e.retry_after + 0.2)

def main():
    app = ApplicationBuilder().token(TOKEN).rate_limiter(AIORateLimiter()).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nickname", nickname_cmd))
    app.add_handler(CommandHandler("lep", lep_cmd))
    app.add_handler(CommandHandler("bind_channel", bind_channel))
    app.add_handler(CommandHandler("post", post_cmd))
    app.add_handler(MessageHandler(filters.FORWARDED & filters.ChatType.PRIVATE, bind_by_forward))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
