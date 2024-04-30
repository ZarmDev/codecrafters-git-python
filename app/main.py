import sys
import os
import zlib

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
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
