from src.qabot.ingest.loader import DocumentLoader
import re
import os
import config


def clean_text(text):
    text = re.sub(r"\[CLS\]|\[SEP\]", "", text)
    text = re.sub(r"\*{1,2}", "", text)
    text = re.sub(r"##\w+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    loader = DocumentLoader()
    results = loader.load_directory(str(config.INPUT_DIR))
    print(f"Found documents: {len(results)}")

    os.makedirs(config.OUTPUT_FILE.parent, exist_ok=True)
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        for doc in results:
            cleaned_text = clean_text(doc.text)
            f.write(f"=== {doc.title} ===\n")
            f.write(f"Path: {doc.path}\n")
            f.write(f"Type: {doc.filetype}\n")
            f.write(f"Updated: {doc.updated_at}\n")
            f.write(f"Text length: {len(cleaned_text)} characters\n")
            f.write("-" * 50 + "\n")
            f.write(cleaned_text + "\n\n")

    print(f"Results saved to {config.OUTPUT_FILE}")


if __name__ == "__main__":
    main()
