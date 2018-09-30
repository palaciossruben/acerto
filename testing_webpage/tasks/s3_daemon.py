import daemon
from s3_uploader import run

with daemon.DaemonContext():
    run()
