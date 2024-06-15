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
    elif command == 'ls-tree':
        '''Just like blobs, tree objects are stored in the .git/objects directory. 
        If the hash of a tree object is e88f7a929cd70b0274c4ea33b209c97fa845fdbc, 
        the path to the object would be ./git/objects/e8/8f7a929cd70b0274c4ea33b209c97fa845fdbc.
        Tree object format:
        tree <size>\0
        <mode> <name>\0<20_byte_sha>
        <mode> <name>\0<20_byte_sha>
        '''
        # First, change the directory to .git/objects 
        givenHash = sys.argv[3]
        # print(sys.argv)
        # Use the first two characters to access the "e8" part
        os.chdir('.git/objects')
        os.chdir(str(givenHash[:2]))
        # Use the second part of the hash to access the file with the tree data
        with open(str(givenHash[2:]), 'rb') as f:
            contents = f.read()
            decompressed_data = zlib.decompress(contents)
            # apparently this is the correct way to split the decompressed data
            firstSplit = decompressed_data.split(b'\0', 1)
            filetype, size = firstSplit[0].decode().split(' ')
            # print(filetype, size)
            '''
            firstSplit has two items:
            0:
            tree <size>
            1:
            <mode> <name>\0<20_byte_sha>
            <mode> <name>\0<20_byte_sha>
            <mode> <name>\0<20_byte_sha>
            <mode> <name>\0<20_byte_sha>
            '''
            '''
            <mode> <name>\0
            <20_byte_sha><mode> <name>\0
            <20_byte_sha><mode> <name>\0
            '''
            # we should expect four items
            # <mode> <name>
            # \0<20_byte_sha>
            #<mode> <name>
            # \0<20_byte_sha>
            otherHalfOfData = firstSplit[1].split(b'\0')
            # do the exception first, and then remove it
            # the exception looks like <mode> <name>\0
            mode, name = otherHalfOfData[0].decode().split(' ')
            print(name)
            # skip first item, since it's an exception
            otherHalfOfData = otherHalfOfData[1:]
            # print(otherHalfOfData)
            for i in otherHalfOfData:
                # i[1] is the sha value
                # all the values here look like <20_byte_sha><mode> <name>\0
                try:
                    mode, name = i[20:].decode().split(' ')
                    # mode, name = i.decode().split(' ')
                    print(name)
                except:
                    None

            # mode, name = firstSplit[1].split(b'\0')[0].decode().split(' ')
            '''
            content looks like:
            
            '''
            # content = content.decode()
            # print(content)
        # Then, access the file using the rest of the hash

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
