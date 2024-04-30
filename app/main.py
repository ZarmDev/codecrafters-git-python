import sys
import os
import zlib
import hashlib

# from https://datagy.io/python-file-size/
def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return int(round(size, 3))

#sha1 - help from AI
def hash_file(file_path):
    sha1 = hashlib.sha1()
    # size in kilobytes
    BUF_SIZE = get_size(file_path)
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        '''
          $ git cat-file -p <blob_sha>
        EX: hello world # This is the contents of the blob
            To implement this, you'll need to:

            Read the contents of the blob object file from the .git/objects directory
            Decompress the contents using Zlib
            Extract the actual "content" from the decompressed data
            Print the content to stdout
        '''
        blob = sys.argv[3]
        os.chdir('.git/objects')
        os.chdir(str(blob[:2]))
        with open(str(blob[2:]), 'rb') as f:
            contents = f.read()
            decompressed_data = zlib.decompress(contents)
            filetype = decompressed_data[0:4].decode()
            size = decompressed_data[5:8].decode()
            content = decompressed_data[8:].decode()
            # prevent newline
            # print(filetype)
            # print(size)
            print(content, end="")
    elif command == "hash-object":
        blob = sys.argv[3]
        blobsize = get_size(blob)
        contents = open(blob, "rb").read()
        new_content = b"blob " + str(blobsize).encode() + b'\0' + contents
        # print(contents)
        # first get the SHA hash of the UNCOMPRESSED contents (including header)
        with open(blob, "wb") as f:
            f.write(new_content)
        hash = hash_file(blob)
        print(hash)
        # then, compress the contents using zlib
        os.chdir('.git/objects/')
        os.mkdir(hash[0:2])
        os.chdir(hash[0:2])
        with open(hash[2:], "wb") as f:
            f.write(zlib.compress(new_content))
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
