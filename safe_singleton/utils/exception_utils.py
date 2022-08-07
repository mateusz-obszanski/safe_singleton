def pretty_error(e: Exception) -> str:
    msg = args[0] if (args := e.args) else None
    suffix = f":{msg}" if msg else ""
    return f"{type(e).__name__}{suffix}"
