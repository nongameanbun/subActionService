from gateway import *
import random

# ─────────────────────────────────────────────
# 문자 → key 클래스 이름 매핑 (inputHandler/HID.py 기준)
# ─────────────────────────────────────────────

# 숫자 → "num0"~"num9"
_DIGIT_MAP = {str(i): f"num{i}" for i in range(10)}

# 소문자 알파벳 → 그대로 ("a"~"z")
_LOWER_MAP = {chr(c): chr(c) for c in range(ord('a'), ord('z') + 1)}

# 기호 → key 클래스 이름 (shift 없이 직접 입력 가능한 것들)
_SYMBOL_MAP = {
    '`':  'backtick',
    '-':  'num_minus',
    '=':  'num_equal',
    '[':  'left_bracket',
    ']':  'right_bracket',
    '\\': 'backslash',
    ';':  'semicolon',
    "'":  'quote',
    ',':  'comma',
    '.':  'period',
    '/':  'slash',
    ' ':  'space',
}

# Shift + 기호 → (base_key_name, True)
# 예: '!' = Shift + '1' → ("num1", True)
_SHIFT_SYMBOL_MAP = {
    '!':  'num1',
    '@':  'num2',
    '#':  'num3',
    '$':  'num4',
    '%':  'num5',
    '^':  'num6',
    '&':  'num7',
    '*':  'num8',
    '(':  'num9',
    ')':  'num0',
    '_':  'num_minus',
    '+':  'num_equal',
    '{':  'left_bracket',
    '}':  'right_bracket',
    '|':  'backslash',
    ':':  'semicolon',
    '"':  'quote',
    '<':  'comma',
    '>':  'period',
    '?':  'slash',
    '~':  'backtick',
}

# ─────────────────────────────────────────────
# 키 입력 헬퍼
# ─────────────────────────────────────────────

def _type_key(key_name, shifted=False):
    """키 하나를 press→release. shifted=True 이면 shift 감싼다."""
    if shifted:
        press_key("left_shift")
        Rdelay_2(5)
    press_key(key_name)
    Rdelay_2(5)
    release_key(key_name)
    Rdelay_2(5)
    if shifted:
        release_key("left_shift")
        Rdelay_2(5)


def _type_char(ch):
    """
    단일 문자를 Arduino HID로 타이핑.
    한글이 아닌 문자(영문, 숫자, 기호, 공백 등)를 처리.
    """
    # 소문자 알파벳
    if ch in _LOWER_MAP:
        _type_key(_LOWER_MAP[ch])
        return

    # 대문자 알파벳 → Shift + 소문자
    if 'A' <= ch <= 'Z':
        _type_key(ch.lower(), shifted=True)
        return

    # 숫자
    if ch in _DIGIT_MAP:
        _type_key(_DIGIT_MAP[ch])
        return

    # 일반 기호 (shift 불필요)
    if ch in _SYMBOL_MAP:
        _type_key(_SYMBOL_MAP[ch])
        return

    # Shift 기호
    if ch in _SHIFT_SYMBOL_MAP:
        _type_key(_SHIFT_SYMBOL_MAP[ch], shifted=True)
        return

    # 알 수 없는 문자 → skip
    print(f"[keyutils] WARNING: unmapped character '{ch}' (U+{ord(ch):04X}), skipped")


# ─────────────────────────────────────────────
# 한글 분해
# ─────────────────────────────────────────────

_HANGUL_START = 0xAC00
_CHOSUNG_BASE = 588
_JUNGSUNG_BASE = 28

_CHOSUNG_LIST = [
    'r', 'R', 's', 'e', 'E', 'f', 'a', 'q', 'Q',
    't', 'T', 'd', 'w', 'W', 'c', 'z', 'x', 'v', 'g'
]
_JUNGSUNG_LIST = [
    'k', 'o', 'i', 'O', 'j', 'p', 'u', 'P', 'h',
    'hk', 'ho', 'hl', 'y', 'n', 'nj', 'np', 'nl',
    'b', 'm', 'ml', 'l'
]
_JONGSUNG_LIST = [
    '', 'r', 'R', 'rt', 's', 'sw', 'sg', 'e', 'f',
    'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'a',
    'q', 'qt', 't', 'T', 'd', 'w', 'c', 'z', 'x', 'v', 'g'
]

_JAMO_MAP = {
    'ㄱ': 'r', 'ㄲ': 'R', 'ㄴ': 's', 'ㄷ': 'e', 'ㄸ': 'E',
    'ㄹ': 'f', 'ㅁ': 'a', 'ㅂ': 'q', 'ㅃ': 'Q', 'ㅅ': 't',
    'ㅆ': 'T', 'ㅇ': 'd', 'ㅈ': 'w', 'ㅉ': 'W', 'ㅊ': 'c',
    'ㅋ': 'z', 'ㅌ': 'x', 'ㅍ': 'v', 'ㅎ': 'g',
    'ㅏ': 'k', 'ㅐ': 'o', 'ㅑ': 'i', 'ㅒ': 'O', 'ㅓ': 'j',
    'ㅔ': 'p', 'ㅕ': 'u', 'ㅖ': 'P', 'ㅗ': 'h', 'ㅘ': 'hk',
    'ㅙ': 'ho', 'ㅚ': 'hl', 'ㅛ': 'y', 'ㅜ': 'n', 'ㅝ': 'nj',
    'ㅞ': 'np', 'ㅟ': 'nl', 'ㅠ': 'b', 'ㅡ': 'm', 'ㅢ': 'ml',
    'ㅣ': 'l'
}

# 쌍자음 매핑 (Shift가 필요한 키)
_SHIFT_JAMO = {'R', 'E', 'Q', 'T', 'W', 'O', 'P'}


def _type_hangul_keys(key_seq):
    """
    한글 2벌식 키 시퀀스('hk', 'R' 등)를 타이핑.
    대문자(쌍자음/이중모음)는 Shift+소문자로 처리.
    """
    for ch in key_seq:
        if ch in _SHIFT_JAMO:
            _type_key(ch.lower(), shifted=True)
        else:
            _type_key(ch)


def _decompose_hangul(char):
    """
    완성형 한글 → 2벌식 키 시퀀스 문자열 반환.
    예: '한' → 'gks'
    """
    code = ord(char) - _HANGUL_START
    cho = code // _CHOSUNG_BASE
    jung = (code % _CHOSUNG_BASE) // _JUNGSUNG_BASE
    jong = code % _JUNGSUNG_BASE
    return _CHOSUNG_LIST[cho] + _JUNGSUNG_LIST[jung] + _JONGSUNG_LIST[jong]


# ─────────────────────────────────────────────
# 메인 입력 함수
# ─────────────────────────────────────────────

def sequence_input(input_sequence, type_per_min=550):
    """
    한글/영문/숫자/기호 혼합 문자열을 Arduino HID로 타이핑.
    """
    for ch in input_sequence:
        code = ord(ch)

        if 0xAC00 <= code <= 0xD7A3:
            # 완성형 한글
            keys = _decompose_hangul(ch)
            _type_hangul_keys(keys)
        elif ch in _JAMO_MAP:
            # 단독 자모
            keys = _JAMO_MAP[ch]
            _type_hangul_keys(keys)
        else:
            # 영문, 숫자, 기호, 공백 등
            _type_char(ch)

        Rdelay_2(int(30000 / type_per_min) if prob(95) else 1000)

    # 엔터
    Rdelay_2(100)
    press_key("enter")
    Rdelay_2(100)
    release_key("enter")
    Rdelay_2(100)


def seq_to_ardu(input_seq):
    for key_name in input_seq:
        seq = key_name
        for k in seq:
            Rdelay_2(5)
            press_key(k)
        Rdelay_2(10)
        for k in reversed(seq):
            Rdelay_2(5)
            release_key(k)
        Rdelay_2(10)


def convert_mode():
    press_key("right_alt")
    Rdelay_2(10)
    release_key("right_alt")
    Rdelay_2(10)

    press_key("s")
    Rdelay_2(50)
    release_key("s")
    Rdelay_2(500)

    press_key("backspace")
    Rdelay_2(50)
    release_key("backspace")
    Rdelay_2(50)


def logout():
    mouse_click("left", 50, random.randint(560, 570), random.randint(770, 780))

    seq = ["up", "enter", "enter"]

    for ch in seq:
        press_key(ch)
        Rdelay_2(100)
        release_key(ch)
        Rdelay_2(100)
        Rdelay_2(3000)

    mouse_click("left", 50, random.randint(55, 65), random.randint(715, 725))

    Rdelay_2(3000)

    press_key("enter")
    Rdelay_2(100)
    release_key("enter")
    Rdelay_2(3000)


def login(id: str, pw: str, type_per_min=550):
    print("login detected")

    # ID 입력
    for ch in id:
        _type_char(ch)
        Rdelay_2(int(30000 / type_per_min) if prob(95) else 1000)

    press_key("tab")
    Rdelay_2(100)
    release_key("tab")
    Rdelay_2(100)

    # PW 입력
    for ch in pw:
        _type_char(ch)
        Rdelay_2(int(30000 / type_per_min) if prob(95) else 1000)

    press_key("enter")
    Rdelay_2(100)
    release_key("enter")
    Rdelay_2(3000)

    # mouse_click("left", 50, random.randint(100, 110), random.randint(604, 608))

    # Rdelay_2(5000)

    # for _ in range(3):
    #     press_key("esc")
    #     Rdelay_2(100)
    #     release_key("esc")
    #     Rdelay_2(1000)

    # mouse_click("left", 50, random.randint(1160, 1165), random.randint(87, 90))