from swift.container.backend import ContainerBroker

import subprocess



command = [
     'find', '/', '-type', 'f',
    '(', '-name', '*.sqlite', '-o', '-name', '*.db', '-o', '-name', '*.sqlite3', ')'
]

# Run the command
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Capture the output and errors
stdout, stderr = process.communicate()

# Check for errors
if process.returncode != 0:
    print()

# Iterate over each line in the output
for line in stdout.splitlines():
    if "containers" in line:
        c = ContainerBroker(line)
        d = c.get_info()
        print(d["bytes_used"])


print()
