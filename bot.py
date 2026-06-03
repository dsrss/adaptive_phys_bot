import logging
import math
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = "8788979720:AAFq69wlkDRNXitQ67fjPGExI0jiRfdZO5c"

CHOOSING_TASK, WAITING_FOR_DATA = range(2)
user_data_store = {}

def get_task_description(task_num):
    descriptions = {
        "1": "B1. Приращение радиус-вектора\nНужно ввести: x1, y1, z1, x2, y2, z2",
        "2": "B2. Вторая производная\nТипы:\n1 - A/z^n + B·ln(z)\n2 - tan²(φ)",
        "3": "B3. Частная производная по y\nФункция: f = (x·z)/y^n + C·z - √y / x\nНужно ввести: n, C",
        "4": "B4. Определённый интеграл ∫₀¹ (A·e^x + B·x²) dx\nНужно ввести: A, B",
        "5": "B5/B6. Модуль вектора d = 2a + b\nНужно ввести: |a|, |b|, угол",
        "6": "B7. Проекции вектора на оси\nНужно ввести: |h|, угол с OX",
        "7": "B8. (a + 2b)²\nНужно ввести: |a|, |b|, угол",
        "8": "B9. Проекция b на a при угле 90°\nНужно ввести: |a|, |b|",
        "9": "B10. Векторное произведение осей\nДанные не нужны, сразу ответ"
    }
    return descriptions.get(task_num, "Неизвестное задание")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу решить часть B по физике.\n\n"
        "Отправь номер задания:\n"
        "1 - B1\n2 - B2\n3 - B3\n4 - B4\n5 - B5/B6\n"
        "6 - B7\n7 - B8\n8 - B9\n9 - B10\n0 - справка"
    )
    return CHOOSING_TASK

async def choose_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text == "0":
        await update.message.reply_text(
            "1 - B1\n2 - B2\n3 - B3\n4 - B4\n5 - B5/B6\n"
            "6 - B7\n7 - B8\n8 - B9\n9 - B10\n\nОтправь номер задания."
        )
        return CHOOSING_TASK
    
    if text not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        await update.message.reply_text("❌ Отправь число от 1 до 9 или 0 для справки.")
        return CHOOSING_TASK
    
    user_data_store[user_id] = {"task": text, "data": [], "step": 0}
    
    if text == "9":
        answer = (
            "=== B10. Векторное произведение осей ===\n"
            "i × j = k\n"
            "j × k = i\n"
            "k × i = j\n"
            "При перестановке — знак минус\n"
            "Направление — по правилу правой руки"
        )
        await update.message.reply_text(answer)
        return CHOOSING_TASK
    
    desc = get_task_description(text)
    await update.message.reply_text(f"{desc}\n\nВводи данные по одному числу. Когда закончишь, напиши 'готово'.")
    
    if text == "1":
        user_data_store[user_id]["expected"] = 6
        await update.message.reply_text("Введи x1:")
    elif text == "2":
        user_data_store[user_id]["expected"] = None
        await update.message.reply_text("Введи тип функции (1 или 2):")
    elif text == "3":
        user_data_store[user_id]["expected"] = 2
        await update.message.reply_text("Введи n:")
    elif text == "4":
        user_data_store[user_id]["expected"] = 2
        await update.message.reply_text("Введи A:")
    elif text == "5":
        user_data_store[user_id]["expected"] = 3
        await update.message.reply_text("Введи |a|:")
    elif text == "6":
        user_data_store[user_id]["expected"] = 2
        await update.message.reply_text("Введи |h|:")
    elif text == "7":
        user_data_store[user_id]["expected"] = 3
        await update.message.reply_text("Введи |a|:")
    elif text == "8":
        user_data_store[user_id]["expected"] = 2
        await update.message.reply_text("Введи |a|:")
    
    return WAITING_FOR_DATA

async def collect_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if user_id not in user_data_store:
        await update.message.reply_text("Начни заново: отправь /start")
        return CHOOSING_TASK
    
    if text.lower() == "готово":
        data = user_data_store[user_id]["data"]
        task = user_data_store[user_id]["task"]
        
        if task == "1":
            if len(data) != 6:
                await update.message.reply_text("Нужно 6 чисел!")
                return WAITING_FOR_DATA
            x1, y1, z1, x2, y2, z2 = data
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            mod = math.sqrt(dx**2 + dy**2 + dz**2)
            answer = (
                f"=== B1. Приращение радиус-вектора ===\n"
                f"Δr = {dx:.4f}i + {dy:.4f}j + {dz:.4f}k\n"
                f"|Δr| = √({dx:.4f}² + {dy:.4f}² + {dz:.4f}²) = {mod:.4f}"
            )
        elif task == "2":
            if len(data) < 1:
                await update.message.reply_text("Введи тип функции")
                return WAITING_FOR_DATA
            tip = int(data[0])
            if tip == 1 and len(data) >= 4:
                A, n, B = data[1], data[2], data[3]
                answer = f"d²r/dz² = {n*(n+1)*A:.4f}/z^{n+2} - {B}/z²"
            elif tip == 2:
                answer = "d²r/dφ² = 2(1+tg²φ)(1+3tg²φ)"
            else:
                answer = "Ошибка"
        elif task == "3":
            if len(data) != 2:
                await update.message.reply_text("Введи n и C")
                return WAITING_FOR_DATA
            n, C = data
            answer = f"∂f/∂y = -{n}·(x·z)/y^{n+1} - 1/(2x√y)"
        elif task == "4":
            if len(data) != 2:
                await update.message.reply_text("Введи A и B")
                return WAITING_FOR_DATA
            A, B = data
            result = A * (math.e - 1) + B / 3
            answer = f"∫₀¹ ({A}·e^x + {B}·x²) dx = {result:.4f}"
        elif task == "5":
            if len(data) != 3:
                await update.message.reply_text("Введи |a|, |b| и угол")
                return WAITING_FOR_DATA
            a, b, angle = data
            rad = math.radians(angle)
            d2 = (2*a)**2 + b**2 + 2 * (2*a) * b * math.cos(rad)
            d = math.sqrt(d2)
            answer = f"|d| = √{d2:.4f} = {d:.4f}"
        elif task == "6":
            if len(data) != 2:
                await update.message.reply_text("Введи |h| и угол")
                return WAITING_FOR_DATA
            h, ang = data
            hx = h * math.cos(math.radians(ang))
            hy = h * math.sin(math.radians(ang))
            answer = f"h_x = {hx:.4f}, h_y = {hy:.4f}"
        elif task == "7":
            if len(data) != 3:
                await update.message.reply_text("Введи |a|, |b| и угол")
                return WAITING_FOR_DATA
            a, b, angle = data
            ab = a * b * math.cos(math.radians(angle))
            res = a**2 + 4*b**2 + 4*ab
            answer = f"(a+2b)² = {res:.4f}"
        elif task == "8":
            if len(data) != 2:
                await update.message.reply_text("Введи |a| и |b|")
                return WAITING_FOR_DATA
            a, b = data
            answer = f"Проекция b на a = {b}·cos90° = 0"
        else:
            answer = "Ошибка"
        
        await update.message.reply_text(answer)
        del user_data_store[user_id]
        return CHOOSING_TASK
    
    try:
        num = float(text)
        user_data_store[user_id]["data"].append(num)
        await update.message.reply_text("Принято. Введи следующее число или 'готово'")
    except ValueError:
        await update.message.reply_text("❌ Введи число или 'готово'")
    
    return WAITING_FOR_DATA

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data_store:
        del user_data_store[user_id]
    await update.message.reply_text("Действие отменено. Отправь /start для начала.")
    return CHOOSING_TASK

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_task)],
            WAITING_FOR_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_data)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()