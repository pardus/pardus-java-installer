import os

_ARCH = ""


def arch():
    global _ARCH
    if not _ARCH:
        _ARCH = "amd64"
        try:
            mainarch = os.uname()[4]
            print("mainarch : {} | arch : {}".format(mainarch, _ARCH))
        except Exception as e:
            mainarch = ""
            print("mainarch Exception : {}".format(e))

        if mainarch == "aarch64":
            _ARCH = "arm64"

    return _ARCH
