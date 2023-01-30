from pathlib import Path
from typing import Optional
from uuid import uuid1

import pandas as pd

from src.utils import QuestionMessageBox, MessageBox

# pyinstaller app.py --windowed --onefile --name "MarcadorDeEntidades" --add-data=pdfjs:.pdfjs
class LabelRegister:
    def __init__(self):
        pass

    def add(self, filename, label, datetime, fieldname, fieldtype):
        filename = str(filename)
        if self.get(filename, fieldname) is not None:
            filename_condition = self.database.filename == filename
            fieldname_condition = self.database.fieldname == fieldname
            self.database.loc[filename_condition & fieldname_condition] = [
                filename,
                label,
                fieldname,
                datetime,
                fieldtype,
            ]
            return
        base_dict = {
            "filename": filename,
            "label": label,
            "datetime": datetime,
            "fieldname": fieldname,
            "fieldtype": fieldtype,
        }
        self.database = self.database.append(base_dict, ignore_index=True)
        self.database.to_csv("marcador_temp.csv", index=False)

    def export(self):
        output_df = pd.DataFrame(
            index=self.database.filename.unique(),
            columns=self.database.fieldname.unique(),
        )
        for filename, label, fieldname, _, _ in self.database.itertuples(index=False):
            output_df.loc[filename, fieldname] = label

        return output_df.reset_index().rename(columns={"index": "arquivo"})

    def get(self, filename: str, fieldname: str, default: Optional[str] = None):
        match = self.database[
            (self.database.fieldname == fieldname)
            & (self.database.filename == str(filename))
        ]
        if match.empty:
            return default
        return match.label.item()

    def load(self):
        log_pth = Path("marcador_temp.csv")
        if log_pth.exists():
            question = QuestionMessageBox(
                "Já existe uma marcação em progresso, continuar com ela?"
            )
            if question.is_yes:
                try:
                    self.database = pd.read_csv(log_pth).fillna("")
                    return
                except Exception:
                    MessageBox("Erro na leitura do arquivo!")
            else:
                log_pth.rename(log_pth.parent / f"{log_pth.stem}_{uuid1()}.csv")
        self.database = pd.DataFrame(
            columns=["filename", "label", "fieldname", "datetime", "fieldtype"]
        )