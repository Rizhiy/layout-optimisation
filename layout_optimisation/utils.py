def process_text(text: str) -> str:
    # Assume that all capital letters can be accessed with shift
    text = text.lower()
    # Change 4 spaces to tabs (python)
    text = text.replace("    ", "\t")
    return text
