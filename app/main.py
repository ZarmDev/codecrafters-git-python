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

def create_tree_object(dir_path):
    print("tree object directory:", dir_path)
    '''
    before Zlib compression:
      tree <size>\0
  <mode> <name>\0<20_byte_sha>
  <mode> <name>\0<20_byte_sha>
  
  For files, the valid values are:
100644 (regular file)
100755 (executable file)
120000 (symbolic link)
For directories, the value is 040000'''
    total_size = 0
    tree_end = ""
    for file in os.listdir(dir_path):
        print(file)
        file_path = os.path.join('.', file)

        mode = None
        # not sure if the exe check works, 
        # not gonna check for exes or symbolic links right now
        if os.path.isfile(file) and not ('.exe' in file):
            mode = "100644"
            file_size = get_size(os.path.abspath(file_path))
            total_size += file_size
        elif os.path.isdir(file):
            mode = "040000"
        sha = hash_file(file_path)
        current_item = f"{mode} {file}\0{sha}"
        tree_end += current_item
    
    tree_object = f"tree {total_size}\0"
    print(tree_object)

# i hope this doesn't brick my pc...
def write_tree_on_each_file_in_directory(directory_name):
    print("working directory!", directory_name)
    # although the name is file, it can be a file or directory
    for file in os.listdir(directory_name):
            print(file)
            # Remember to ignore the .git directory when creating entries in the tree object.
            if file == '.git':
                continue
            sha_hash = None
            file_path = os.path.join('.', file)
            # If the entry is a file, create a blob object and record its SHA hash
            if os.path.isfile(file):
                with open(file, 'rb') as f:
                    blobsize = get_size(file_path)
                    contents = open(file_path, "rb").read()
                    blob_object = b"blob " + str(blobsize).encode() + b'\0' + contents
                    # first get the SHA hash of the UNCOMPRESSED contents (including header)
                    sha_hash = hash_file(file_path)
                    # print(sha_hash)
            # If the entry is a directory, recursively create a tree object and record its SHA hash
            elif os.path.isdir(file):
                ## Create the tree object ##
                '''
                <mode> <name>\0
                <20_byte_sha><mode> <name>\0
                <20_byte_sha><mode> <name>\0
                '''
                create_tree_object(file_path)
                

def main():
    command = sys.argv[1]
    thirdargument = None
    try:
        thirdargument = sys.argv[3]
    except:
        pass
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
        os.chdir('.git/objects')
        os.chdir(str(thirdargument[:2]))
        with open(str(thirdargument[2:]), 'rb') as f:
            contents = f.read()
            decompressed_data = zlib.decompress(contents)
            filetype = decompressed_data[0:4].decode()
            size = decompressed_data[5:8].decode()
            content = decompressed_data[8:].decode()
            print(content, end="")
    elif command == "hash-object":
        blobsize = get_size(thirdargument)
        contents = open(thirdargument, "rb").read()
        blob_object = b"blob " + str(blobsize).encode() + b'\0' + contents
        # print(contents)
        # first get the SHA hash of the UNCOMPRESSED contents (including header)
        with open(thirdargument, "wb") as f:
            f.write(blob_object)
        sha_hash = hash_file(thirdargument)
        print(sha_hash)
        # then, compress the contents using zlib
        os.chdir('.git/objects/')
        os.mkdir(sha_hash[0:2])
        os.chdir(sha_hash[0:2])
        with open(sha_hash[2:], "wb") as f:
            f.write(zlib.compress(blob_object))
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
        # print(sys.argv)
        # Use the first two characters to access the "e8" part
        os.chdir('.git/objects')
        os.chdir(str(thirdargument[:2]))
        # Use the second part of the hash to access the file with the tree data
        with open(str(thirdargument[2:]), 'rb') as f:
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
                    # print(name)
                except:
                    None
    elif command == 'write-tree':
        # Iterate over the files/directories in the working directory
        workingdirectory = os.getcwd()
        write_tree_on_each_file_in_directory(workingdirectory)
        ## TODO: Once you have all the entries and their SHA hashes, write the tree object to the .git/objects directory
        # .git/objects/<first 2 chars of sha>/<remaining chars of sha>
        os.chdir('.git/objects')
        os.chdir(sha_hash[:2])
        with open(sha_hash[2:], "wb") as f:
            pass
                    
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
