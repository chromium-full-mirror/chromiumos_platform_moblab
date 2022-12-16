import os
from os.path import expanduser
from typing import Iterable
import argparse
import sys
import json
import re
import multiprocessing
from multiprocessing.pool import ThreadPool
from google.api_core import page_iterator
from google.cloud.storage import Client as GcsClient

path_where_key_is_stored = expanduser(
    "~/.gsutil/moblab_login/chromeos-partner-moblab-account-login.json"
)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_where_key_is_stored

def readable_size(byte: int) -> str:
    kb = round(byte / 1024, 1)
    mb = round(kb / 1024, 1)
    gb = round(mb / 1024, 1)
    tb = round(gb / 1024, 1)

    if tb > 1.0:
        return f"{tb} TB"
    elif gb > 1.0:
        return f"{gb} GB"
    elif mb > 1.0:
        return f"{mb} MB"
    else:
        return f"{kb} KB"

class FileInfo(object):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


class DirectoryInfo(object):
    def __init__(self, name: str):
        self.sub_directories = {}
        self.files = []
        self.name = name
        self.size = 0
    
    def get_sub_directory(self, name: str):
        return self.sub_directories.get(name)
    
    def add_directory(self, name: str):
        d = DirectoryInfo(name)
        self.sub_directories[name] = d
        return d
    
    def add_file(self, file: FileInfo):
        self.files.append(file)
    
    def add_size(self, size: int):
        self.size += size


class GcsBucketService():
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.storage_client = GcsClient()
        self.bucket_info = None
        self.error_message = []
        self.fetch_bucket_info()

    
    def list_directories(self, prefix: str="", filter_func=None) -> list:
        try:
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            extra_params = {"prefix": prefix, "delimiter": "/"}
            path = "/b/" + self.bucket_name + "/o"
            iterator = page_iterator.HTTPIterator(
                client=self.storage_client,
                api_request=self.storage_client._connection.api_request,
                path=path,
                items_key="prefixes",
                item_to_value=lambda _, item: item,
                extra_params=extra_params,
            )
            return list(filter(filter_func, iterator))
        except Exception as e:
            self.error_message.append({"list_directories": e})


    def list_blobs(self, prefix: str="", delimiter: str="", page_size: int=None, fields: str=None) -> Iterable:
        try:
            if prefix and not prefix.endswith("/"):
                prefix += "/"
            blobs = self.storage_client.list_blobs(bucket_or_name=self.bucket_name, prefix=prefix, delimiter=delimiter, page_size=page_size, fields=fields)
            return blobs
        except Exception as e:
            self.error_message.append({"list_blobs": e})


    def list_boards(self) -> list:
        try:
            directories = self.list_directories(filter_func=lambda x: x.endswith("-release/"))
            return directories # ['brask-release/', 'brya-release/']
        except Exception as e:
            self.error_message.append({"list_boards": e})
    

    def list_boards_by_os_image_amount(self) -> list:
        try:
            def find_os_image_amount(board: str):
                os_images = self.list_directories(prefix=board)
                return (board, len(os_images))
            
            boards = self.list_boards()
            thread_count = multiprocessing.cpu_count()
            thread_pool = ThreadPool(thread_count)
            board_list = thread_pool.map(find_os_image_amount, boards)
            sorted_board_list = list(map(lambda x: x[0].split("/")[0], sorted(board_list, key = lambda x: x[1], reverse=True)))
            return sorted_board_list
        except Exception as e:
            self.error_message.append({"list_boards_by_os_image_amount": e})


    def get_os_images_info_by_board(self, board: str):
        root_directory = DirectoryInfo(name=board)
        try:
            blobs = self.list_blobs(prefix=board, page_size=10000, fields="items(name, size), nextPageToken")

            def check_milestone_build_format(path):
                result = re.search("R([0-9]{2,3})-([0-9]{5,}\.[0-9]{1,}\.[0-9]{1,})", path)
                return False if result == None else True

            def add_milestone_to_path(paths):
                board = paths.pop(0)
                milestone_build = paths.pop(0)
                milestone = milestone_build.split("-")[0]
                build = milestone_build.split("-")[1]
                paths.insert(0, build)
                paths.insert(0, milestone)
                paths.insert(0, board)
                return paths

            for blob in blobs:
                paths = blob.name.split("/")
                if check_milestone_build_format(paths[1]):
                    paths = add_milestone_to_path(paths)
                file = FileInfo(name=paths[-1], size=blob.size)

                current_directory = root_directory
                current_directory.add_size(file.size)

                for p in paths[1:-1]:
                    temp_directory = current_directory
                    current_directory = temp_directory.get_sub_directory(p)
                    if not current_directory:
                        current_directory = temp_directory.add_directory(p)

                    current_directory.add_size(file.size)

                current_directory.add_file(file)
            return root_directory
        except Exception as e:
            self.error_message.append({"get_os_images_info_by_board": f"\"{board}\" problem: {e}"})
            return root_directory
            

    def fetch_bucket_info(self):
        try:
            thread_count = multiprocessing.cpu_count()
            thread_pool = ThreadPool(thread_count)
            boards = self.list_boards_by_os_image_amount()
            boards_info = thread_pool.map(self.get_os_images_info_by_board, boards)
            self.bucket_info = DirectoryInfo(self.bucket_name)

            for board in boards_info:
                self.bucket_info.sub_directories[board.name] = board
                self.bucket_info.size += board.size
        except Exception as e:
            self.error_message.append({"fetch_bucket_info": e})


class Printer:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.gcs_bucket_service = GcsBucketService(bucket_name=bucket_name)
        self.root_path = f"{self.bucket_name}"
        self.current_path_stack = [self.root_path]
        self.current_path_info = self.gcs_bucket_service.bucket_info
        self.get_gcs_bucket_service_error_message()
    
    def get_gcs_bucket_service_error_message(self):
        gcs_bucket_service_error_message = self.gcs_bucket_service.error_message
        if gcs_bucket_service_error_message:
            for message in gcs_bucket_service_error_message:
                print(message)

    def get_now_path(self):
        return f"/{'/'.join(self.current_path_stack)}"

    def update_current_path_info(self) -> bool:
        now_path = ""
        try:
            self.current_path_info = self.gcs_bucket_service.bucket_info
            for path in self.current_path_stack[1:]:
                now_path = path
                self.current_path_info = self.current_path_info.sub_directories[path]
            return True
        except KeyError as e:
            print(f"cd: no such file or directory: {now_path}")
            return False


    def level_up(self):
        if len(self.current_path_stack) == 1 and self.current_path_stack[0] == self.root_path:
            return
        self.current_path_stack.pop()
        self.update_current_path_info()


    def level_down(self, path: str):
        origin_path_stack = self.current_path_stack[:]
        if path and path.startswith("/"):
            path = path[1:]
        paths = path.split("/")
        self.current_path_stack.extend(paths)
        update_result = self.update_current_path_info()
        if not update_result:
            self.current_path_stack.clear()
            self.current_path_stack.extend(origin_path_stack)
        

    def get_bucket_size(self):
        print(f"\nBucket \"{self.gcs_bucket_service.bucket_name}\" size is {readable_size(self.gcs_bucket_service.bucket_info.size)}.")
    

    def list_dir(self, show_size=False):
        for dir in self.current_path_info.sub_directories.values():
            if show_size:
                size = readable_size(dir.size)
                print(f"{dir.name : <30}{size : >30}")
            else:
                print(f"{dir.name}")
        for file in self.current_path_info.files:
            if show_size:
                size = readable_size(file.size)
                print(f"{file.name : <50}{size : >50}")
            else:
                print(f"{file.name}")

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bucket",
        type=str
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    try:
        args = parse_args(sys.argv[1:])
        bucket_name = args.bucket
        printer = Printer(bucket_name=bucket_name)

        print("\nYou can type command \"help\" to see what command you can use. Or you can use ctrl + c to exit.\n")
        while True:
            now_path = printer.get_now_path()
            command = (input(f"{now_path} >")).strip()
            if command == "help":
                print("\nls -> list folder")
                print("\nls -s -> list folder and see its size")
                print("\ncd .. -> return to upper folder")
                print("\ncd {folder name or path} -> into folder")
            elif command == "ls -s":
                printer.list_dir(show_size=True)
            elif command == "ls":
                printer.list_dir(show_size=False)
            elif command == "cd ..":
                printer.level_up()
            elif command.startswith("cd "):
                path = (command.split(" ")[1]).strip()
                printer.level_down(path)
            else:
                print("No this command")

    except KeyboardInterrupt as e:
        print("exit")
        raise KeyboardInterrupt