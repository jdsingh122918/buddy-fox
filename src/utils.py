"""
Utility functions and formatters for Buddy Fox agent.
"""

import json
import re
from typing import Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., "1m 23s", "45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}h {minutes}m"


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp to human-readable string.

    Args:
        timestamp: Datetime object (None = now)

    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 MB", "500 KB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from text.

    Args:
        text: Text to extract URLs from

    Returns:
        list[str]: List of URLs found
    """
    url_pattern = r"https?://[^\s<>\"']+"
    return re.findall(url_pattern, text)


def clean_url(url: str) -> str:
    """
    Clean and normalize URL.

    Args:
        url: URL to clean

    Returns:
        str: Cleaned URL
    """
    # Remove trailing slashes
    url = url.rstrip("/")

    # Remove common tracking parameters
    tracking_params = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]

    if "?" in url:
        base_url, query = url.split("?", 1)
        params = [p for p in query.split("&") if not any(p.startswith(f"{tp}=") for tp in tracking_params)]
        if params:
            url = f"{base_url}?{'&'.join(params)}"
        else:
            url = base_url

    return url


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        str or None: Domain name
    """
    pattern = r"https?://(?:www\.)?([^/]+)"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def format_cost(cost_usd: float) -> str:
    """
    Format cost in USD.

    Args:
        cost_usd: Cost in USD

    Returns:
        str: Formatted cost (e.g., "$0.05", "$1.23")
    """
    if cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    return f"${cost_usd:.2f}"


def format_tokens(tokens: int) -> str:
    """
    Format token count with thousands separator.

    Args:
        tokens: Number of tokens

    Returns:
        str: Formatted token count (e.g., "1,234")
    """
    return f"{tokens:,}"


def parse_markdown_links(text: str) -> list[tuple[str, str]]:
    """
    Parse markdown links from text.

    Args:
        text: Text with markdown links

    Returns:
        list[tuple[str, str]]: List of (link_text, url) tuples
    """
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    return re.findall(pattern, text)


def create_markdown_link(text: str, url: str) -> str:
    """
    Create a markdown link.

    Args:
        text: Link text
        url: URL

    Returns:
        str: Markdown link
    """
    return f"[{text}]({url})"


def load_json(file_path: Path) -> Any:
    """
    Load JSON from file.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(data: Any, file_path: Path, indent: int = 2) -> None:
    """
    Save data to JSON file.

    Args:
        data: Data to save
        file_path: Path to save to
        indent: JSON indentation
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent)


def format_list(items: list[str], max_items: int = 5, prefix: str = "- ") -> str:
    """
    Format list of items as bullet points.

    Args:
        items: List of items
        max_items: Maximum items to show
        prefix: Prefix for each item

    Returns:
        str: Formatted list
    """
    if not items:
        return ""

    shown_items = items[:max_items]
    result = "\n".join(f"{prefix}{item}" for item in shown_items)

    if len(items) > max_items:
        remaining = len(items) - max_items
        result += f"\n{prefix}... and {remaining} more"

    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Filename to sanitize

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name_len = 250 - len(ext)
        filename = f"{name[:max_name_len]}.{ext}" if ext else name[:255]

    return filename


def split_text_by_tokens(
    text: str, max_tokens: int = 1000, estimate_ratio: float = 0.25
) -> list[str]:
    """
    Split text into chunks by estimated token count.

    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk
        estimate_ratio: Estimated tokens per character ratio

    Returns:
        list[str]: List of text chunks
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = int(max_tokens / estimate_ratio)

    if len(text) <= max_chars:
        return [text]

    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        para_length = len(para)

        if current_length + para_length > max_chars and current_chunk:
            # Start new chunk
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_length = para_length
        else:
            current_chunk.append(para)
            current_length += para_length

    # Add remaining chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def create_progress_bar(
    current: int, total: int, width: int = 40, fill_char: str = "█", empty_char: str = "░"
) -> str:
    """
    Create a text-based progress bar.

    Args:
        current: Current progress
        total: Total amount
        width: Width of progress bar in characters
        fill_char: Character for filled portion
        empty_char: Character for empty portion

    Returns:
        str: Progress bar string
    """
    if total == 0:
        return f"[{empty_char * width}] 0%"

    percent = current / total
    filled = int(width * percent)
    empty = width - filled

    bar = f"{fill_char * filled}{empty_char * empty}"
    percentage = int(percent * 100)

    return f"[{bar}] {percentage}%"


def highlight_text(text: str, color: str = "blue") -> str:
    """
    Add ANSI color codes to text for terminal highlighting.

    Args:
        text: Text to highlight
        color: Color name (red, green, blue, yellow, etc.)

    Returns:
        str: Text with ANSI color codes
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }
    reset = "\033[0m"

    color_code = colors.get(color.lower(), "")
    return f"{color_code}{text}{reset}" if color_code else text


def strip_ansi_codes(text: str) -> str:
    """
    Remove ANSI color codes from text.

    Args:
        text: Text with ANSI codes

    Returns:
        str: Text without ANSI codes
    """
    ansi_pattern = r"\033\[[0-9;]*m"
    return re.sub(ansi_pattern, "", text)
