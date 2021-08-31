import logging
import json

logger = logging.getLogger(__name__)


def number(s):
    return "".join(list(filter(lambda x: x.isnumeric() or x == '.', s)))


def isfloat(s):
    if "." not in s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def process(s):
    s = list(map(lambda x: x.lower(), s.split(" ")))
    clean_s = []
    for i in s:
        tmp = "".join(
            list(filter(lambda x: x.isalpha() or isfloat(x) or x == '.', i)))
        if len(tmp.strip()) >= 1:
            clean_s.append(tmp)

    return clean_s


def get_amount(all_text, axis=1):
    word_list = ["debit", "total", "payment", "amount", "credit", ]

    all_text.sort(key=lambda x: x["Center"][axis])
    text_price = []
    for pos, text in enumerate(all_text):
        closest = (1, "")
        if isfloat(text["Text"]):
            continue
        for look in range(pos, len(all_text)):
            if abs(text["Center"][axis] - all_text[look]["Center"][axis]) > 0.02:
                break
            if isfloat(number(all_text[look]["Text"])):
                closest = min(closest, (abs(
                    text["Center"][axis] - all_text[look]["Center"][axis]), all_text[look]["Text"]))
        for look in range(pos, 0, -1):
            if abs(text["Center"][axis] - all_text[look]["Center"][axis]) > 0.02:
                break
            if isfloat(number(all_text[look]["Text"])):
                closest = min(closest, (abs(
                    text["Center"][axis] - all_text[look]["Center"][axis]), all_text[look]["Text"]))

        if closest[1] != "":
            text_price.append((text["Text"], closest[1]))


    for w in word_list:
        for t in text_price[::-1]:
            if w in process(t[0]):
                return float(number(t[1]))

    all_amnt = set()
    for t in text_price:
        if "$" in t[1]:
            amnt = float(number(t[1]))
            all_amnt.add(amnt)

    return max(list(all_amnt))


'''
    Given a directory with receipt file and OCR output, this function should extract the amount
    Parameters:
    dirpath (str): directory path containing receipt and ocr output
    Returns:
    float: returns the extracted amount
'''

def extract_amount(dirpath: str) -> float:
    logger.info('extract_amount called for dir %s', dirpath)

    # your logic goes here

    with open(f'{dirpath}/ocr.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_text = []

    for block in data["Blocks"]:
        if "Text" in block:
            cx = block["Geometry"]["BoundingBox"]["Left"] + \
                block["Geometry"]["BoundingBox"]["Width"]/2
            cy = block["Geometry"]["BoundingBox"]["Top"] + \
                block["Geometry"]["BoundingBox"]["Height"]/2
            all_text.append({"Text": block["Text"], "Center": (cx, cy)})

    yaxis = get_amount(all_text, axis=1)
    if yaxis != -1:
        return yaxis

    return 0.0