import paramiko
from tempfile import NamedTemporaryFile

server = sys.stdin.readline()
username = sys.stdin.readline()
password = sys.stdin.readline()

ssh = paramiko.SSHClient()
ssh.connect(server, username=username, password=password)
magma_code = ""
for line in sys.stdin:
  if line == "<EOF>\n":
    with NamedTemporaryFile() as infile:
      infile.write(magma_code)
      ssh.exec_command("magma {0}".format(infile.name))
      ssh.recv_exit_status()
    with open('magma_helper_out.magma', 'r') as outfile:
      print(outfile.read().replace('\n',': '))
    magma_code = ""

  elif line == "<DONE>\n":
    break

  else:
    magma_code = magma_code + line
