def convJaSpell(term):
    if "Vengeance" in term:
        return "報復"
    elif "Bloody" in term:
        return "血刃の狩猟"
    elif "Flame" in term:
        return "炎撃の狩猟"
    elif "Retribution" in term:
        return "狩猟"
    elif "Petrify" in term:
        return "石化"
    elif "Sprint" in term:
        return "アサルト"
    elif "Inspire" in term:
        return "インスパイア"
    else:
        return term

def convJaBuild(term):
    if "Twilight" in term:
        return "トワイライトアーマー"
    elif "Cursed" in term:
        return "カースヘルム"
    elif "Immortality" in term:
        return "イモータル"
    elif "Molten" in term:
        return "メルトエッセンス"
    elif "Legplates" in term:
        return "スチールレッグプレート"
    elif "Blade" in term:
        return "ブレードアーマー"
    elif "Dominance" in term:
        return "ドミナントシールド"
    elif "Brute" in term:
        return "ブレストプレート"
    elif "Guardian" in term:
        return "守り人の兜"
    elif "Queen's" in term:
        return "クイーンウィング"
    elif "Haas's" in term:
        return "ブラッドクロー"
    elif "Rose Gold Meteor" in term:
        return "デモンフォール"
    else:
        return term

def convJaCreep(term):
    if "Lord" in term:
        return "ロード"