from dataclasses import dataclass

@dataclass
class AddLinkCommand:
    url: str

@dataclass
class DeleteLinkCommand:
    url: str
