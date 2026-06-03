// АДАПТИВНЫЙ КУРС ФИЗИКИ — БОТ ДЛЯ TELEGRAM (Cloudflare Workers)
// Рабочая версия для деплоя на Cloudflare Workers

const BOT_TOKEN = '8788979720:AAFq69wlkDRNXitQ67fjPGExI0jiRfdZO5c';

// Состояния пользователей
const userStates = new Map();

// Отправка сообщения
async function sendMessage(chatId, text) {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
    try {
        await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id: chatId, text: text })
        });
    } catch (e) {
        console.error('Send error:', e);
    }
}

// Описания заданий
function getTaskDesc(taskNum) {
    const desc = {
        '1': '📐 B1. Приращение радиус-вектора\nВведи x1, y1, z1, x2, y2, z2 (каждое число отдельно)',
        '2': '📐 B2. Вторая производная\nТипы:\n1 — A/z^n + B·ln(z)\n2 — tan²(φ)',
        '3': '📐 B3. Частная производная по y\nВведи n и C',
        '4': '📐 B4. Интеграл ∫₀¹ (A·e^x + B·x²) dx\nВведи A и B',
        '5': '📐 B5/B6. Модуль вектора d = 2a + b\nВведи |a|, |b| и угол (градусы)',
        '6': '📐 B7. Проекции вектора\nВведи |h| и угол с OX (градусы)',
        '7': '📐 B8. (a + 2b)²\nВведи |a|, |b| и угол (градусы)',
        '8': '📐 B9. Проекция b на a при 90°\nВведи |a| и |b|',
        '9': '📐 B10. Векторное произведение осей'
    };
    return desc[taskNum] || '❌ Неизвестное задание';
}

// Расчёты
function calcB1(data) {
    const [x1,y1,z1,x2,y2,z2] = data;
    const dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
    const mod = Math.hypot(dx, dy, dz);
    return `Δr = ${dx}i + ${dy}j + ${dz}k\n|Δr| = ${mod.toFixed(4)}`;
}

function calcB2(data) {
    if (data[0] == 1) {
        const A = data[1], n = data[2], B = data[3];
        return `d²r/dz² = ${n*(n+1)*A}/z^{n+2} - ${B}/z²`;
    }
    return `d²r/dφ² = 2(1+tg²φ)(1+3tg²φ)`;
}

function calcB3(data) {
    const n = data[0];
    return `∂f/∂y = -${n}·(x·z)/y^{n+1} - 1/(2x√y)`;
}

function calcB4(data) {
    const A = data[0], B = data[1];
    const result = A * (Math.E - 1) + B / 3;
    return `∫₀¹ (${A}·e^x + ${B}·x²) dx = ${result.toFixed(4)}`;
}

function calcB56(data) {
    const a = data[0], b = data[1], angle = data[2];
    const rad = angle * Math.PI / 180;
    const d2 = (2*a)**2 + b**2 + 4*a*b*Math.cos(rad);
    return `|d| = ${Math.sqrt(d2).toFixed(4)}`;
}

function calcB7(data) {
    const h = data[0], ang = data[1];
    const rad = ang * Math.PI / 180;
    const hx = h * Math.cos(rad);
    const hy = h * Math.sin(rad);
    return `h_x = ${hx.toFixed(4)}, h_y = ${hy.toFixed(4)}`;
}

function calcB8(data) {
    const a = data[0], b = data[1], angle = data[2];
    const rad = angle * Math.PI / 180;
    const ab = a * b * Math.cos(rad);
    const result = a*a + 4*b*b + 4*ab;
    return `(a+2b)² = ${result.toFixed(4)}`;
}

function calcB9() {
    return `Проекция b на a = 0 (cos90° = 0)`;
}

function calcB10() {
    return `i × j = k\nj × k = i\nk × i = j\nНаправление — по правилу правой руки`;
}

// Обработка сообщений
async function handleUpdate(update) {
    const chatId = update.message?.chat?.id;
    const text = update.message?.text?.trim();
    if (!chatId || !text) return;

    // Начало диалога
    if (!userStates.has(chatId)) {
        if (text === '/start') {
            await sendMessage(chatId, 
                '👋 Привет! Я бот по физике (часть B).\n\n'
                + '📌 Отправь номер задания:\n'
                + '1 — B1\n2 — B2\n3 — B3\n4 — B4\n5 — B5/B6\n'
                + '6 — B7\n7 — B8\n8 — B9\n9 — B10');
            return;
        }
        
        // Проверка выбора задания
        if (['1','2','3','4','5','6','7','8','9'].includes(text)) {
            if (text === '9') {
                await sendMessage(chatId, calcB10());
                return;
            }
            userStates.set(chatId, { task: text, data: [] });
            await sendMessage(chatId, getTaskDesc(text));
            
            const firstParam = {
                '1': 'x1', '2': 'тип (1 или 2)', '3': 'n', '4': 'A',
                '5': '|a|', '6': '|h|', '7': '|a|', '8': '|a|'
            }[text];
            await sendMessage(chatId, `Введи ${firstParam}:`);
            return;
        }
        
        await sendMessage(chatId, '❌ Отправь /start и выбери задание 1–9');
        return;
    }

    // Пользователь в процессе ввода
    const state = userStates.get(chatId);
    
    if (text.toLowerCase() === 'готово') {
        let answer = '';
        try {
            switch(state.task) {
                case '1': answer = calcB1(state.data); break;
                case '2': answer = calcB2(state.data); break;
                case '3': answer = calcB3(state.data); break;
                case '4': answer = calcB4(state.data); break;
                case '5': answer = calcB56(state.data); break;
                case '6': answer = calcB7(state.data); break;
                case '7': answer = calcB8(state.data); break;
                case '8': answer = calcB9(); break;
                default: answer = 'Ошибка';
            }
        } catch(e) {
            answer = '❌ Ошибка при вычислении. Проверь введённые данные.';
        }
        await sendMessage(chatId, answer);
        userStates.delete(chatId);
        return;
    }

    // Сбор чисел
    const num = parseFloat(text);
    if (isNaN(num)) {
        await sendMessage(chatId, '❌ Введи число или "готово"');
        return;
    }
    state.data.push(num);
    
    // Подсказка следующего параметра
    const prompts = {
        '1': ['x1','y1','z1','x2','y2','z2'],
        '2': ['тип','A','n','B'],
        '3': ['n','C'],
        '4': ['A','B'],
        '5': ['|a|','|b|','угол'],
        '6': ['|h|','угол'],
        '7': ['|a|','|b|','угол'],
        '8': ['|a|','|b|']
    };
    const taskPrompts = prompts[state.task];
    
    if (taskPrompts && state.data.length < taskPrompts.length) {
        await sendMessage(chatId, `Введи ${taskPrompts[state.data.length]}:`);
    } else {
        await sendMessage(chatId, 'Введи "готово" для расчёта');
    }
}

// Основной обработчик
export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        
        if (url.pathname === '/webhook' && request.method === 'POST') {
            const update = await request.json();
            ctx.waitUntil(handleUpdate(update));
            return new Response('OK', { status: 200 });
        }
        
        if (url.pathname === '/webhook') {
            return new Response('Webhook is ready!', { status: 200 });
        }
        
        return new Response('Bot is running on Cloudflare Workers!', { status: 200 });
    }
};
