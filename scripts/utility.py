import subprocess
import os

# Get the original user when run with sudo
SUDO_USER = os.getenv("SUDO_USER")
if SUDO_USER:
    HOME_DIR = os.path.expanduser(f"~{SUDO_USER}")
else:
    HOME_DIR = os.path.expanduser("~")

# Folder management functions
USER_DIRS_FILE = os.path.join(HOME_DIR, ".config/user-dirs.dirs")

DEFAULT_DIRS = {
    "XDG_DESKTOP_DIR": f"{HOME_DIR}/Desktop",
    "XDG_DOWNLOAD_DIR": f"{HOME_DIR}/Downloads",
    "XDG_TEMPLATES_DIR": f"{HOME_DIR}/Templates",
    "XDG_PUBLICSHARE_DIR": f"{HOME_DIR}/Public",
    "XDG_DOCUMENTS_DIR": f"{HOME_DIR}/Documents",
    "XDG_MUSIC_DIR": f"{HOME_DIR}/Music",
    "XDG_PICTURES_DIR": f"{HOME_DIR}/Pictures",
    "XDG_VIDEOS_DIR": f"{HOME_DIR}/Videos"
}

def read_user_dirs():
    if not os.path.exists(USER_DIRS_FILE):
        return "No custom folder configurations found. Using defaults.", DEFAULT_DIRS.copy()
    user_dirs = {}
    with open(USER_DIRS_FILE, "r") as file:
        for line in file:
            if line.startswith("XDG_") and "=" in line:
                key, value = line.strip().split("=")
                folder = value.strip('"')
                user_dirs[key] = folder
    return "Custom folder configurations loaded.", user_dirs

def save_user_dirs(updated_dirs):
    lines = []
    if os.path.exists(USER_DIRS_FILE):
        with open(USER_DIRS_FILE, "r") as file:
            lines = file.readlines()
    with open(USER_DIRS_FILE, "w") as file:
        for line in lines:
            if not any(line.startswith(key) for key in updated_dirs):
                file.write(line)
        for key, value in updated_dirs.items():
            file.write(f'{key}="{value}"\n')
    return "User folder configurations saved."

def apply_default_dirs():
    with open(USER_DIRS_FILE, "w") as file:
        for key, value in DEFAULT_DIRS.items():
            file.write(f'{key}="{value}"\n')
    return "Default folder configurations applied."

# System installation functions
def perform_basic_installation():
    subprocess.run(["sudo", "apt", "update", "-y"])
    subprocess.run(["sudo", "apt", "install", "-y", "software-properties-common"])
    subprocess.run(["sudo", "apt", "upgrade", "-y", "--fix-missing"])
    subprocess.run(["sudo", "apt", "install", "-y", 
                  "vim", "nano", "curl", "wget", "git", "htop", "dkms"])

def install_kvm_packages():
    subprocess.run(["sudo", "apt", "install", "-y", "qemu-kvm", "libvirt-daemon-system", "virtinst", "virt-manager"])
    subprocess.run(["sudo", "usermod", "-aG", "libvirt,kvm", os.getenv("SUDO_USER", os.getlogin())])
    subprocess.run(["sudo", "systemctl", "enable", "--now", "libvirtd"])

def setup_software_managers():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "gnome-software"])
    subprocess.run(["sudo", "apt", "install", "-y", "synaptic"])
    subprocess.run(["sudo", "apt", "install", "-y", "snapd"])
    subprocess.run(["sudo", "systemctl", "enable", "--now", "snapd"])
    subprocess.run(["sudo", "ln", "-s", "/var/lib/snapd/snap", "/snap"])

def install_wine_winetricks():
    subprocess.run(["sudo", "dpkg", "--add-architecture", "i386"])
    subprocess.run(["sudo", "mkdir", "-p", "/etc/apt/keyrings"])
    subprocess.run(["sudo", "wget", "-O", "/etc/apt/keyrings/winehq-archive.key", 
                   "https://dl.winehq.org/wine-builds/winehq.key"])
    subprocess.run(["sudo", "wget", "-NP", "/etc/apt/sources.list.d/", 
                   "https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources"])
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "--install-recommends", "winehq-stable"])
    subprocess.run(["sudo", "apt", "install", "-y", "winetricks"])

def install_python_packages():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", 
                   "python3.10", "python3-pip", "python3.10-venv",
                   "build-essential", "llvm", "clang"])

# Hardware optimization functions
def amd_cpu_setup():
    subprocess.run(["sudo", "apt", "install", "-y", "amd64-microcode"])

def intel_cpu_setup():
    subprocess.run(["sudo", "apt", "install", "-y", "intel-microcode"])

def amdgpu_non_rocm_setup():
    subprocess.run(["sudo", "apt", "install", "-y", "xserver-xorg-video-amdgpu", "vulkan-tools", "mesa-vulkan-drivers"])

def amdgpu_rocm_setup():
    with open("/etc/apt/sources.list.d/rocm.list", "w") as f:
        f.write("deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.7 jammy main\n")
    subprocess.run(
        "wget -qO- https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm.gpg",
        shell=True,
        check=True
    )
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "rocm-dkms"])
    subprocess.run(["sudo", "usermod", "-a", "-G", "video,render", os.getenv("SUDO_USER", os.getlogin())])

def nvidia_gpu_setup():
    subprocess.run(["sudo", "apt", "install", "-y", "ubuntu-drivers-common"])
    subprocess.run(["sudo", "add-apt-repository", "-y", "ppa:graphics-drivers/ppa"])
    driver = subprocess.getoutput("ubuntu-drivers devices | grep -oP 'driver : \\K\\S+' | head -1")
    if not driver:
        driver = "nvidia-driver-515"
    subprocess.run(["sudo", "apt", "install", "-y", driver, "dkms"])
    print("\nWARNING: Secure Boot key enrollment required after reboot!")

def arm64_firmware_setup():
    subprocess.run(["sudo", "add-apt-repository", "-y", "multiverse"])
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "qcom-firmware-extract"])

def intel_gpu_setup():
    subprocess.run(["sudo", "apt", "install", "-y", "intel-media-va-driver-non-free"])

# System tweak functions
def check_sudo_nopasswd():
    file_path = "/etc/sudoers.d/nopasswd"
    if not os.path.exists(file_path):
        return False
    user = os.getenv("SUDO_USER", os.getlogin())
    with open(file_path, "r") as f:
        return f"{user} ALL=(ALL) NOPASSWD: ALL" in f.read()

def toggle_sudo_nopasswd():
    user = os.getenv("SUDO_USER", os.getlogin())
    file_path = "/etc/sudoers.d/nopasswd"
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        content = f"{user} ALL=(ALL) NOPASSWD: ALL\n"
        with open(file_path, "w") as f:
            f.write(content)
        os.chmod(file_path, 0o440)
        # Validate sudoers syntax
        result = subprocess.run(["visudo", "-c", "-f", file_path], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            os.remove(file_path)
            raise Exception(f"Invalid sudoers syntax: {result.stderr.strip()}")

def check_auto_login():
    with open("/etc/gdm3/custom.conf", "r") as f:
        return f"AutomaticLogin={os.getenv('SUDO_USER', os.getlogin())}" in f.read()

def toggle_auto_login():
    user = os.getenv("SUDO_USER", os.getlogin())
    if check_auto_login():
        subprocess.run(["sudo", "sed", "-i", f"s/^AutomaticLogin={user}/#  AutomaticLogin/", "/etc/gdm3/custom.conf"])
    else:
        subprocess.run(["sudo", "sed", "-i", f"s/^#  AutomaticLogin/AutomaticLogin={user}/", "/etc/gdm3/custom.conf"])

def check_windows_commands():
    return os.path.exists("/etc/profile.d/windows_commands.sh")

def implement_windows_commands():
    with open("/tmp/windows_commands.sh", "w") as f:
        f.write("""\
function dir() { ls -l "$@"; }
function copy() { cp -i "$@"; }
function move() { mv -i "$@"; }
function del() { rm -i "$@"; }
function md() { mkdir -p "$@"; }
function rd() { rmdir "$@"; }
function cls() { clear; }
function type() { cat "$@"; }
function where() { which "$@"; }
function echo() { printf "%s\\n" "$*"; }
function shutdown() { sudo shutdown -h now; }
function restart() { sudo shutdown -r now; }
""")
    subprocess.run(["sudo", "mv", "/tmp/windows_commands.sh", "/etc/profile.d/windows_commands.sh"])
    subprocess.run(["sudo", "chmod", "+x", "/etc/profile.d/windows_commands.sh"])

def get_hang_timeout():
    try:
        user = os.getenv("SUDO_USER", os.getlogin())
        uid = subprocess.check_output(["id", "-u", user]).decode().strip()
        output = subprocess.check_output(
            ["sudo", "-u", user, "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/" + uid + "/bus",
             "gsettings", "get", "org.gnome.mutter", "check-alive-timeout"],
            text=True
        ).strip()
        return int(output.replace("uint32 ", "")) // 1000
    except:
        return 5

def adjust_hang_timeout():
    current = get_hang_timeout()
    new_seconds = input(f"Enter new timeout in seconds (current: {current}, 0=disable): ").strip()
    if not new_seconds.isdigit():
        print("Invalid input. Must be a number.")
        return
    new_milliseconds = int(new_seconds) * 1000
    user = os.getenv("SUDO_USER", os.getlogin())
    uid = subprocess.check_output(["id", "-u", user]).decode().strip()
    subprocess.run([
        "sudo", "-u", user, "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/" + uid + "/bus",
        "gsettings", "set", "org.gnome.mutter", "check-alive-timeout", f"uint32 {new_milliseconds}"
    ])