import platform

def get():
    if platform.machine().endswith("64"):
        return "TV"
    else:
        return "tablet"