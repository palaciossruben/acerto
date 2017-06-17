import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


def simple_upload(request):
    """Saves file on machine resumes/* file system"""

    if request.method == 'POST' and request.FILES['curriculum']:
        myfile = request.FILES['curriculum']
        fs = FileSystemStorage()

        # TODO: make this dynamic
        user_id = '100'
        folder = os.path.join('subscribe/resumes', user_id)

        # create file path:
        if not os.path.isdir(folder):
            os.mkdir(folder)

        file_path = os.path.join(folder, myfile.name)

        fs.save(file_path, myfile)

        fs.url(file_path)
        return render(request, 'upload_file/simple_upload.html')

    return render(request, 'upload_file/simple_upload.html')
