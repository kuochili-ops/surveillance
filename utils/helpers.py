def normalize_text(text):
    if not text:
        return ""
    return (
        str(text).lower()
        .replace(" ", "")
        .replace("劑", "")
        .replace("注射液劑", "注射液")
        .replace("毫克", "mg")
        .replace("毫升", "ml")
    )
