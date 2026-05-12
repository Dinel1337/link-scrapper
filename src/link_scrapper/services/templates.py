"""Горячие клавиши для вставки заготовленных сообщений."""
from link_scrapper.domain.text import FirstMessage, SecondMessage, ThirdMessage, FourthMessage, FifthMessage, SixthMessage, SeventhMessage, BaseMessage  
import keyboard

MESSAGE_CLASSES = [
    FirstMessage,
    SecondMessage,
    ThirdMessage,
    FourthMessage,
    FifthMessage,
    SixthMessage,
    SeventhMessage,
]

_current_index = 0

def generate_template(idx: int) -> str:
    """Создаёт случайное сообщение из класса с индексом idx."""
    cls = MESSAGE_CLASSES[idx % len(MESSAGE_CLASSES)]
    return cls().build()

def _cycle_template():
    """Вставляет следующее сообщение по кругу."""
    global _current_index
    text = generate_template(_current_index)
    keyboard.write(text, delay=0.02)
    print(f"  [{_current_index+1}/{len(MESSAGE_CLASSES)}] {text}")
    _current_index = (_current_index + 1) % len(MESSAGE_CLASSES)

def register_templates():
    """Вешает Insert на циклическую вставку."""
    keyboard.add_hotkey('insert', _cycle_template)
    print(f"Loaded {len(MESSAGE_CLASSES)} message classes. Press Insert to cycle:")
    for i, cls in enumerate(MESSAGE_CLASSES):
        print(f"  {i+1}. {cls.__name__}")
