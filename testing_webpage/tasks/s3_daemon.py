import daemon
from tasks.s3_uploader import run

with daemon.DaemonContext():
    run()
