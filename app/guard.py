import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|"
    r"call|do|set|reset|vacuum|lock|pg_sleep|pg_read_file|pg_ls_dir|"
    r"lo_import|lo_export|dblink)\b",
    re.IGNORECASE,
)

def is_safe(sql: str) -> bool:
    s = sql.strip().rstrip(";")
    if ";" in s:
        return False
    if not s.lower().startswith(("select", "with")):
        return False
    return not FORBIDDEN.search(s)