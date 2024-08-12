from swift.container.backend import ContainerBroker

import subprocess

def get_dbs():
    command = [
        'find', '/', '-type', 'f',
        '(', '-name', '*.sqlite', '-o', '-name', '*.db', '-o', '-name', '*.sqlite3', ')'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print()
    return stdout.splitlines()

# # Iterate over each line in the output
# for line in stdout.splitlines():
#     if "containers" in line:
#         c = ContainerBroker(line)
#         d = c.get_info()
#         print(d["bytes_used"])


# print()
import pathlib

root = pathlib.Path("/home")
a = list(root.rglob("*containers*.db"))
print()
