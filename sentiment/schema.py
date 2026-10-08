from dataclasses import asdict, dataclass


@dataclass
class SentimentItem:
    title: str
    summary: str
    source: str
    publish_time: str
    url: str
    tag: str

    def to_dict(self):
        return asdict(self)
