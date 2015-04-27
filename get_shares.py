import cerealizer
import sys
import os
import subprocess
def main():

    if len(sys.argv) != 3:
        raise Exception("Incorrect args")
    main_dir = sys.argv[1]
    method = sys.argv[2]

    allfiles = []
    for root, dirs, files in os.walk(main_dir):
        #considering main dir has bunch of directories with each testing data
        matched = []
        if len(files) != 0:
            for smallfile in files:
                matched.append(os.path.join(root, smallfile))
            allfiles.append(matched)

    for metafiles in allfiles:
        for single_filename in metafiles:
            #print("single filename " + str(single_filename))
            parser = single_filename.split("/")[-1]
            parser = parser.split(".pdf")[0]
            print(parser)
            subprocess.call(
                ["./main.py",
                str(5), str(2), str(2),
                single_filename, 'new_version/' + str(parser) + ".hex",
                method
            ])

if __name__ == "__main__":
    main()
