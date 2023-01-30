from dataclasses import dataclass
from typing import Any, List, Optional
from enum import Enum

from src.utils import (
    FieldLabelEmptyError,
    FieldDuplicateLabelError,
    FieldMethodNotValid,
)


class FieldType(str, Enum):
    CLASSIFCATION = "Classificação"
    EXTRACTION = "Extração"


@dataclass
class Field:
    name: str
    type: FieldType
    labels: Optional[List[str]] = None

    def __post_init__(self):
        if self.type == FieldType.EXTRACTION:
            self.labels = None
        else:
            self.labels = []

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "labels": self.labels,
        }

    @property
    def is_extraction(self):
        return self.type == FieldType.EXTRACTION

    @classmethod
    def from_dict(cls, dict):
        return cls(
            name=dict["name"],
            type=dict["type"],
            labels=dict["labels"],
        )

    def add_label(self, label: str) -> None:
        self.validate(label)
        self.labels.append(label)

    def validate(self, label: str) -> None:
        if label == "":
            raise FieldLabelEmptyError(
                "Label is empty string, please provide a value or delete the field."
            )
        if self.type == FieldType.EXTRACTION:
            raise FieldMethodNotValid("Can't add label to extraction field")
        if label in self.labels:
            raise FieldDuplicateLabelError(
                "This field has the same label more than once."
            )


@dataclass
class FieldRegister:
    database: Any

    def remove(self, field_name: str) -> None:
        self.database = self.database[self.database.name != field_name]

    def add(self, field: Field) -> None:
        self.validate(field)
        base_dict = field.to_dict()
        base_dict["is_drawn"] = 0
        self.database = self.database.append(base_dict, ignore_index=True)

    def validate(self, field) -> None:
        if field.name == "":
            raise Exception("No field name given!")
        if field.name in self.database.name:
            raise Exception("This field name is already in use!")
        if field.type == FieldType.CLASSIFCATION:
            if len(field.labels) == 0:
                raise Exception(
                    "Classification fields must have at least one label, you provided none."
                )

    def is_valid_name(self, field_name: str) -> None:
        return field_name != "" and field_name not in self.database.name

    def undrawn(self):
        for row in self.database[self.database["is_drawn"] == 0].itertuples():
            yield Field.from_dict(row._asdict())
        self.database.loc[self.database["is_drawn"] == 0, "is_drawn"] = 1

    def __iter__(self):
        for row in self.database.itertuples():
            yield Field.from_dict(row._asdict())