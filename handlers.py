# coding: utf-8
from tornado import web
import os
import re
from tornado import httputil


class UploadHandlers(web.RequestHandler):

    def get(self):
        in_file = os.path.join(self.get_template_path(), "index.html")
        with open(in_file, "rb") as f:
            for a in f.readlines():
                self.write(a)

    def post(self):
        # ignore delete
        print(self.request)
        content_range = re.split('/| |-', self.request.headers.get('Content-Range'))
        for i in range(1, 4):
            content_range[i] = int(content_range[i])
        print(content_range)
        if 'files[]' in self.request.files:
            for file in self.request.files['files[]']:
                # print(self.request.headers.get('Content-Range'))
                files = self.handle_file_upload(file['filename'], file['body'], content_range)
        elif 'file' in self.request.files:
            file = self.request.files['file']
            files = self.handle_file_upload(file['filename'], file['body'], content_range)

        self.set_header("Content-Type", "text/plain")
        self.write(self.generate_response({'files': files}))

    def generate_response(self, content):
        return content

    def handle_file_upload(self, name, body, content_range):
        file = dict()
        file_path = self.get_upload_path(name)
        file_path = self.get_unique_name(file_path, content_range[1])
        file['name'] = file_path
        file['size'] = content_range
        file['type'] = None

        # append_file = content_range and os.path.exists(file_path) and (file['size'] > os.path.getsize(file_path))
        with open(file_path, "ab") as fout:
            fout.write(body)
        file['size'] = os.path.getsize(file_path)
        return file

    def get_upload_path(self, name):
        return name

    def get_unique_name(self, name, size):
        while os.path.exists(name) and (not os.path.isfile(name)):
            name = self.upcount_name(name)
        while os.path.isfile(name):
            if os.path.getsize(name) == size:
                break
            name = self.upcount_name(name)
        return name

    def upcount_name(self, name):
        split_name = os.path.splitext(name)
        regex = '[(]([0-9]+)[)]$'
        match = re.search(regex, split_name[0])
        if match:
            split_name[0], number = re.subn(regex, '(' + str(int(match.group(1)) + 1) + ')', split_name[0])
        else:
            split_name[0] += ' (1)'
        return split_name[0] + split_name[1]


default_handlers = [
    (r"/upload_handlers", UploadHandlers),
]
