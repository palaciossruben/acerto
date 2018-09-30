import daemon
from tasks.s3_uploader import upload_all

with daemon.DaemonContext():
    upload_all()
