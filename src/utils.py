import logging


def time_str_to_seconds(time_str: str):
    try:
        if "s" in time_str:
            return int(time_str.replace("s", ""))
        elif "m" in time_str:
            return int(time_str.replace("m", "")) * 60
        elif "h" in time_str:
            return int(time_str.replace("h", "")) * 60 * 60
        else:
            return int(time_str)
    except ValueError:
        logging.error(f"Invalid time string {time_str}")
        return None


def time_seconds_to_str(time_seconds: int):
    if time_seconds < 60:
        return f"{time_seconds}s"
    elif time_seconds < 60 * 60:
        return f"{time_seconds // 60}m " \
            f"{time_seconds % 60}s"
    else:
        return f"{time_seconds // (60 * 60)}h " \
            f"{(time_seconds % (60 * 60)) // 60}m " \
            f"{(time_seconds % (60 * 60)) % 60}s"
