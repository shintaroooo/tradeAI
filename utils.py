import re

def extract_broker_recommendation(text: str):
    match = re.search(r"【おすすめFX業者】：(.+?)\n【理由】：(.+)", text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

def remove_broker_section(text: str):
    return re.sub(r"【おすすめFX業者】：.+?\n【理由】：.+", "", text, flags=re.DOTALL).strip()

