import json
import logging
import os

from colorama import Fore, Style


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
        return f"{round(time_seconds, 2)}s"
    elif time_seconds < 60 * 60:
        return f"{int(time_seconds // 60)}m " \
            f"{round(time_seconds % 60, 2)}s"
    else:
        return f"{int(time_seconds // (60 * 60))}h " \
            f"{(int(time_seconds % (60 * 60)) // 60)}m " \
            f"{round(time_seconds % (60 * 60) % 60, 2)}s"


def create_stats_file():
    if not os.path.exists("stats.json"):
        print(
            f"{Fore.CYAN}Stats file "
            f"({Fore.BLUE}stats.json{Fore.CYAN}) not found..."
            f"\n{Fore.CYAN}Creating stats file...{Style.RESET_ALL}"
        )
        update_stats(0, 0, 0, 0, 0, 0, 0)
    else:
        print(
            f"{Fore.CYAN}Stats file "
            f"({Fore.BLUE}stats.json{Fore.CYAN}) already exists!"
        )


def get_stats():
    time_running = 0
    messages_sent = 0
    messages_failed = 0
    times_failed = 0
    time_sending = 0
    time_retrying = 0
    current_position = 0
    if not os.path.exists("stats.json"):
        create_stats_file()
    print(Fore.CYAN + "Loading stats file..." + Style.RESET_ALL)

    with open("stats.json", "r") as f:
        stats = json.loads(f.read())
        time_running = stats["time_running"]
        messages_sent = stats["messages_sent"]
        messages_failed = stats["messages_failed"]
        times_failed = stats["times_failed"]
        time_sending = stats["time_sending"]
        time_retrying = stats["time_retrying"],
        current_position = stats["current_position"]
        f.close()
    print(Fore.CYAN + "Stats loaded from " +
          Fore.BLUE + "stats.json" + Style.RESET_ALL)
    return (
        time_running,
        messages_sent,
        messages_failed,
        times_failed,
        time_sending,
        time_retrying,
        current_position
    )


def update_stats(time_running, messages_sent, messages_failed, times_failed,
                 time_sending, time_retrying, current_position):
    stats = {
        "time_running": time_running,
        "messages_sent": messages_sent,
        "messages_failed": messages_failed,
        "times_failed": times_failed,
        "time_sending": time_sending,
        "time_retrying": time_retrying,
        "current_position": current_position,
    }
    with open("stats.json", "w") as f:
        f.write(json.dumps(stats, indent=4))
        f.close()
        
def backup_stats():
    time_running, messages_sent, messages_failed, times_failed, time_sending, time_retrying, current_position = get_stats()
    with open(f"stats_backup_{current_position}.json", "w") as f:
        f.write(json.dumps({
            "time_running": time_running,
            "messages_sent": messages_sent,
            "messages_failed": messages_failed,
            "times_failed": times_failed,
            "time_sending": time_sending,
            "time_retrying": time_retrying,
            "current_position": current_position,
        }, indent=4))
        f.close()
    print(f"{Fore.CYAN}Stats backed up to {Fore.BLUE}stats_backup_{current_position}.json{Style.RESET_ALL}")


def get_stats_message():
    from src.config import Config
    (time_running, messages_sent, messages_failed,
     times_failed, time_sending, time_retrying) = get_stats()
    config = Config()
    config.load_config()

    time_waited = (
        time_running - time_sending-time_retrying
    )
    avg_send_time = time_sending / messages_sent \
        if messages_sent > 0 else 0
    avg_wait_time = (
        (time_waited) /
        (messages_sent + messages_failed)
    )
    avg_retry_time = time_retrying / times_failed \
        if times_failed > 0 else 0
    success_rate = messages_sent / (
        messages_sent + messages_failed
    ) * 100 if messages_sent + messages_failed > 0 else 0

    title_color = Fore.LIGHTRED_EX
    header_color = Fore.LIGHTBLUE_EX
    stat_color = Fore.LIGHTYELLOW_EX
    value_color = Fore.LIGHTMAGENTA_EX
    bullet = f"{Fore.LIGHTBLACK_EX}  ★  {Style.RESET_ALL}"
    br = (
        f"\n{Fore.LIGHTWHITE_EX}"
        f"\n────────────────────────────────────────\n\n"
        f"{Style.RESET_ALL}"
    )

    header = f"{title_color}          Messaging Statistics{Style.RESET_ALL}"
    sent_stats = get_sent_statistics(header_color, stat_color, value_color,
                                     bullet, messages_sent, time_sending,
                                     avg_send_time, success_rate)
    failed_stats = get_failed_statistics(
        header_color, stat_color, value_color, bullet, messages_failed,
        times_failed, time_retrying, avg_retry_time
    )
    other_stats = get_other_statistics(
        header_color, stat_color, value_color, bullet, time_waited,
        avg_wait_time, config.max_time, config.max_messages, time_running,
        messages_sent
    )
    return (
        f"{br}{header}{br}{sent_stats}{br}"
        f"{failed_stats}{br}{other_stats}{br}"
    )


def get_sent_statistics(
    header_color: Fore,
    stat_color: Fore,
    value_color: Fore,
    bullet: str,
    messages_sent: int,
    time_sending: float,
    avg_send_time: float,
    success_rate: float
):
    return (
        f"{Fore.LIGHTBLACK_EX}───{header_color} Sent Message Statistics:"
        f"\n{bullet}{stat_color}Messages Sent: "
        f"{value_color}{messages_sent}"
        f"\n{bullet}{stat_color}Time Spent Sending: "
        f"{value_color}{time_seconds_to_str(time_sending)}"
        f"\n{bullet}{stat_color}Average Time to Send: "
        f"{value_color}{time_seconds_to_str(avg_send_time)}"
        f"\n{bullet}{stat_color}Success Rate: "
        f"{value_color}{success_rate}%{Style.RESET_ALL}"
    )


def get_failed_statistics(
    header_color: Fore,
    stat_color: Fore,
    value_color: Fore,
    bullet: str,
    messages_failed: int,
    times_failed: int,
    time_retrying: float,
    avg_retry_time: float
):
    return (
        f"{Fore.LIGHTBLACK_EX}───{header_color} Failed Message Statistics:"
        f"\n{bullet}{stat_color}Messages Failed: "
        f"{value_color}{messages_failed}"
        f"\n{bullet}{stat_color}Times Failed/Retried: "
        f"{value_color}{times_failed}"
        f"\n{bullet}{stat_color}Time Spent Retrying: "
        f"{value_color}{time_seconds_to_str(time_retrying)}"
        f"\n{bullet}{stat_color}Average Time to Retry: "
        f"{value_color}{time_seconds_to_str(avg_retry_time)}{Style.RESET_ALL}"
    )


def get_other_statistics(
    header_color: Fore,
    stat_color: Fore,
    value_color: Fore,
    bullet: str,
    time_waited: float,
    avg_wait_time: float,
    max_time: int,
    max_messages: int,
    time_running: float,
    messages_sent: int
):
    remaining_time_val = ""
    remaining_messages_val = ""
    if max_time != -1:
        remaining_time = time_seconds_to_str(max_time - time_running)
        remaining_time_val = (
            f"\n{bullet}{stat_color}Remaining time: "
            f"{value_color}{remaining_time}{Style.RESET_ALL}"
        )
    if max_messages != -1:
        remaining_messages = max_messages - messages_sent
        remaining_messages_val = (
            f"\n{bullet}{stat_color}Remaining messages: "
            f"{value_color}{remaining_messages}{Style.RESET_ALL}"
        )
    return (
        f"{Fore.LIGHTBLACK_EX}───{header_color} "
        f"Other Statistics:{Style.RESET_ALL}"
        f"\n{bullet}{stat_color}Time Waited: "
        f"{value_color}{time_seconds_to_str(time_waited)}"
        f"\n{bullet}{stat_color}Average Wait Time: "
        f"{value_color}{time_seconds_to_str(avg_wait_time)}{Style.RESET_ALL}"
        f"{remaining_time_val}"
        f"{remaining_messages_val}"
    )
