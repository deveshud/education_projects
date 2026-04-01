from pathlib import Path

folder = Path("unstructured_data_ingestion\\data")

print(list(folder.glob("*.docx")))