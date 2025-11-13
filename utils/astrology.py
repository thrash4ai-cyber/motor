
from datetime import date
SIGNS = [
    ((3,21),(4,19),"Овен"),((4,20),(5,20),"Телец"),((5,21),(6,20),"Близнецы"),
    ((6,21),(7,22),"Рак"),((7,23),(8,22),"Лев"),((8,23),(9,22),"Дева"),
    ((9,23),(10,22),"Весы"),((10,23),(11,21),"Скорпион"),((11,22),(12,21),"Стрелец"),
    ((12,22),(1,19),"Козерог"),((1,20),(2,18),"Водолей"),((2,19),(3,20),"Рыбы"),
]
def zodiac_sign(d: date) -> str:
    m, day = d.month, d.day
    for (sm, sd), (em, ed), name in SIGNS:
        if sm <= em:
            if (m > sm or (m == sm and day >= sd)) and (m < em or (m == em and day <= ed)):
                return name
        else:
            if (m > sm or (m == sm and day >= sd)) or (m < em or (m == em and day <= ed)):
                return name
    return "Неизвестно"
