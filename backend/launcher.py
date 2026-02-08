
import subprocess

with open("launcher_output.txt", "w") as outfile:
    subprocess.run(["python", "debug_client_creation.py"], stdout=outfile, stderr=outfile, text=True)
