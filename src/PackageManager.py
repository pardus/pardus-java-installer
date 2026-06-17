import os
import subprocess

from gi.repository import Gio, GLib

import Arch

CWD = os.path.dirname(os.path.abspath(__file__))
ACTIONS_PY = f"{CWD}/Actions.py"


# "apt-package": {"name":"Display Name", "path":"java binary path", "javaws_path":"javaws path"}
PACKAGES = {
    "openjdk-25-jre": {
        "name": "OpenJDK 25",
        "path": ["/usr/lib/jvm/java-25-openjdk-{}/bin/java".format(Arch.arch())],
        "architectures": ["amd64", "arm64"],
    },
    "openjdk-21-jre": {
        "name": "OpenJDK 21",
        "path": ["/usr/lib/jvm/java-21-openjdk-{}/bin/java".format(Arch.arch())],
        "architectures": ["amd64", "arm64"],
    },
    "jdk-25": {
        "name": "Oracle Java 25",
        "path": [
            "/usr/lib/jvm/jdk-25.0.2-oracle-x64/bin/java",
            "/usr/lib/jvm/jdk-25-oracle-x64/bin/java",
        ],
        "architectures": ["amd64", "arm64"],
    },
    "jdk-11": {
        "name": "Oracle Java 11",
        "path": ["/usr/lib/jvm/jdk-11.0.30-oracle-x64/bin/java"],
        "architectures": ["amd64", "arm64"],
    },
    "oracle-java8-jdk": {
        "name": "Oracle Java 8",
        "path": ["/usr/lib/jvm/oracle-java8-jdk-{}/jre/bin/java".format(Arch.arch())],
        "javaws_path": [
            "/usr/lib/jvm/oracle-java8-jdk-{}/jre/bin/javaws".format(Arch.arch())
        ],
        "architectures": ["amd64", "arm64"],
    },
}

COMMANDS = {
    "install": ["apt", "install", "==PACKAGE==", "-yq", "-o", "APT::Status-Fd=1"],
    "remove": ["apt", "purge", "==PACKAGE==", "-yq"],
    "make-default": ["update-alternatives", "--set", "java", "==PATH=="],
    "make-default-javaws": ["update-alternatives", "--set", "javaws", "==PATH=="],
    "update-alternatives-auto": ["update-alternatives", "--auto", "java"],
}


def get_command(operation, package=None, path=None):
    if operation in COMMANDS:
        cmd = COMMANDS[operation].copy()

        if package and package in PACKAGES:
            cmd = list(map(lambda x: package if x == "==PACKAGE==" else x, cmd))

            if path and path in PACKAGES[package]["path"]:
                cmd = list(map(lambda x: path if x == "==PATH==" else x, cmd))

            return cmd

    return None


def get_package_info(package):
    if package in PACKAGES:
        return PACKAGES[package]
    return None


def has_package(package):
    return package in PACKAGES


class PackageManager:
    def __init__(self, on_process_finished, on_progress):
        # Get packages array
        self.on_process_finished = on_process_finished
        self.on_progress = on_progress

        self.default_java_path = ""
        self.default_javaws_path = ""

        # Get initialize infos:
        self.find_default()
        self.find_default_javaws()

    def install(self, package):
        package_info = get_package_info(package)
        if not package_info:
            return

        self.run_action("install", package)
        self.on_progress("%0", "Downloading")

    def uninstall(self, package):
        package_info = get_package_info(package)
        if not package_info:
            return

        if self.is_default(package):
            self.run_action("update-alternatives-auto", package)
            self.run_action("remove", package)
        else:
            self.run_action("remove", package)

    def set_as_default(self, package):
        package_info = get_package_info(package)
        if not package_info:
            return

        # Get java path
        path = next((p for p in package_info["path"] if os.path.exists(p)), None)

        self.run_action("make-default", package, path)
        if "javaws_path" in package_info:
            if not self.is_default_javaws(package):
                path_javaws = next(
                    (p for p in package_info["path"] if os.path.exists(p)), None
                )
                self.run_action("make-default-javaws", package, path_javaws)

    # CHECK BOOLEANS:
    def is_installed(self, package):
        if not has_package(package):
            return

        p = subprocess.run(["dpkg", "-s", package], capture_output=True)

        # Return exit status
        return p.returncode == 0

    def is_default(self, package):
        package_info = get_package_info(package)
        if not package_info:
            return False

        for path in package_info["path"]:
            if path == self.default_java_path:
                return True
        return False

    def is_default_javaws(self, package):
        package_info = get_package_info(package)
        if not package_info:
            return False

        for path in package_info["javaws_path"]:
            if path == self.default_javaws_path:
                return True
        return False

    # TOOLS:
    def find_default(self):
        p = subprocess.run(
            ["update-alternatives", "--query", "java"], capture_output=True, text=True
        )

        if p.returncode != 0:
            return

        for l in p.stdout.splitlines():
            line = l.split(": ")
            if str(line[0]) == "Value":
                self.default_java_path = line[1]
                return

    def find_default_javaws(self):
        p = subprocess.run(
            ["update-alternatives", "--query", "javaws"], capture_output=True, text=True
        )

        if p.returncode != 0:
            return

        for l in p.stdout.splitlines():
            line = l.split(": ")
            if str(line[0]) == "Value":
                self.default_javaws_path = line[1]
                return

    # PROCESS SPAWNING:
    def run_action(self, operation, package, path=None):
        print(f"-- Running action: {operation}, {package}, path={path}")
        if path:
            self.start_process(
                ["/usr/bin/pkexec", ACTIONS_PY, operation, package, path]
            )
        else:
            self.start_process(["/usr/bin/pkexec", ACTIONS_PY, operation, package])

    def start_process(self, params):
        p = Gio.Subprocess.new(params, Gio.SubprocessFlags.STDOUT_PIPE)

        stdout_stream = Gio.DataInputStream.new(p.get_stdout_pipe())

        def read_stdout(stream):
            stream.read_line_async(GLib.PRIORITY_DEFAULT, None, stdout_callback)

        def stdout_callback(stream, result):
            try:
                line, length = stream.read_line_finish_utf8(result)

                if line is None:
                    return  # EOF

                params = line.split(":")

                if "dlstatus" in params:
                    self.on_progress(f"%{params[2].split('.')[0]}", "Downloading")
                elif "pmstatus" in params:
                    self.on_progress(params[3].rstrip(), "Installing")

                read_stdout(stream)

            except GLib.Error as e:
                print("stdout error:", e)

        def process_finished(proc, result):
            try:
                success = proc.wait_finish(result)
                exit_code = proc.get_exit_status()

                self.on_process_finished(exit_code)

            except GLib.Error as e:
                print("process error:", e)

        read_stdout(stdout_stream)
        p.wait_async(None, process_finished)
