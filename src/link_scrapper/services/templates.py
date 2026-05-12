from link_scrapper.domain.text import FirstMessage, SecondMessage, ThirdMessage, FourthMessage, FifthMessage, SixthMessage, SeventhMessage

MESSAGE_CLASSES = [FirstMessage, SecondMessage, ThirdMessage, FourthMessage,
                   FifthMessage, SixthMessage, SeventhMessage]

def generate_message(index: int) -> str:
    """Возвращает сообщение, выбранное по индексу (циклически)."""
    cls = MESSAGE_CLASSES[index % len(MESSAGE_CLASSES)]
    return cls().build()