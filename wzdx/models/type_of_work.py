from dataclasses import dataclass
import json
from wzdx.models.enums import WorkTypeName


@dataclass
class TypeOfWork:
    type_name: WorkTypeName
    is_architectural_change: bool

    def to_dict(self):
        return {
            "type_name": self.type_name.value,
            "is_architectural_change": self.is_architectural_change,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(data: str) -> "TypeOfWork":
        obj = json.loads(data)
        return TypeOfWork(
            type_name=WorkTypeName(obj["type_name"]),
            is_architectural_change=obj["is_architectural_change"],
        )
