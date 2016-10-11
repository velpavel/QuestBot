import math

def text_lower_wo_command(message):
    if message.text:
        text = message.text.lower()
    else:
        text = ''
    if text.startswith('/'): text=text[1:]
    return text

def Distance(llat1, llong1,llat2,llong2):
    """Вычисление растояния в метрах между координатами"""
    #pi - число pi, rad - радиус сферы (Земли)
    rad = 6372795
    #в радианах
    lat1 = llat1*math.pi/180.
    lat2 = llat2*math.pi/180.
    long1 = llong1*math.pi/180.
    long2 = llong2*math.pi/180.

    #косинусы и синусы широт и разницы долгот
    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    #вычисления длины большого круга
    y = math.sqrt(math.pow(cl2*sdelta,2)+math.pow(cl1*sl2-sl1*cl2*cdelta,2))
    x = sl1*sl2+cl1*cl2*cdelta
    ad = math.atan2(y,x)
    dist = ad*rad
    return round(dist)