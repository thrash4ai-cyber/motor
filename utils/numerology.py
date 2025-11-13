
from datetime import date, datetime
def parse_date(text: str):
    text = text.strip()
    for f in ("%Y-%m-%d", "%d.%m.%Y"):
        try: return datetime.strptime(text, f).date()
        except ValueError: pass
    return None
def digit_sum(n: int) -> int:
    s = 0
    while n > 0: s, n = s + (n % 10), n // 10
    return s
def reduce_num(n: int) -> int:
    while n > 22 or (n not in (11, 22) and n > 9):
        n = digit_sum(n)
    return n
def life_path(birth: date) -> int:
    return reduce_num(int(birth.strftime("%Y%m%d")))
def day_number(d: date) -> int:
    return reduce_num(int(d.strftime("%Y%m%d")))
def energy_of_day(birth: date, today: date) -> dict:
    lp, dn = life_path(birth), day_number(today)
    mix = reduce_num(lp + dn)
    meanings = {
        1:"Старт, инициатива, личное лидерство.",
        2:"Дипломатия, партнёрства, мягкий темп.",
        3:"Коммуникации, идеи, лёгкий прогресс.",
        4:"Структура, дисциплина, шаг за шагом.",
        5:"Изменения, движение, эксперименты (аккуратнее с рисками).",
        6:"Отношения, семья, ответственность и забота.",
        7:"Фокус, обучение, внутренняя ясность важнее спешки.",
        8:"Воля, деньги, результатная концентрация.",
        9:"Завершение, эмпатия, отпускание лишнего.",
        11:"Интуиция на пике; будь избирателен, береги энергию.",
        22:"Мастер-постройка: планируй крупно, закрепляй на практике.",
    }
    return {"life_path": lp, "day_num": dn, "mix": mix, "meaning": meanings.get(mix, "Баланс и осознанность.")}
def compatibility_score(d1: date, d2: date) -> dict:
    lp1, lp2 = life_path(d1), life_path(d2)
    harmony = 70 + (10 if lp1 == lp2 else 0)
    if {lp1, lp2} in ({2,8}, {4,8}, {1,6}): harmony += 8
    if {lp1, lp2} in ({3,7}, {4,5}): harmony -= 10
    harmony = max(0, min(100, harmony))
    return {"lp1": lp1, "lp2": lp2, "score": harmony,
            "risk":"Следи за балансом «жёсткость ↔ чувствительность»; избегай ультиматумов 48 часов.",
            "tip":"Согласуйте 1–2 общих шага на 14 дней; проговорите ожидания простыми фразами."}
