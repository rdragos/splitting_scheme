import cerealizer
import sys
import subprocess

def get_first_share(secret, no_parties, threshold, block_size):
    sh_int = [int(str(x), 16) for x in secret]
    f = open("pdf_test.in", "wb")
    f.write(bytearray(sh_int))
    f.close()

    subprocess.call(["./main.py", str(no_parties), str(threshold), str(block_size), "pdf_test.in", "shares_dump.out"])

    allshares = cerealizer.load(open("shares_dump.out", "rb"))
    #return only the first poly
    return [tp for tp in allshares]

def evaluate(file_type):
    if file_type is 0:
        return "doc"
    elif file_type is 1:
        return "gif"
    elif file_type is 2:
        return "pdf"
    elif file_type is 3:
        return "png"
    elif file_type is 4:
        return "ppt"
    elif file_type is 5:
        return "rar"
    elif file_type is 6:
        return "zip"

def main():

    doc_hex = ['D0', 'CF', '11', 'E0']
    gif_hex = ['47', '49', '46', '38']
    pdf_hex = ['25', '50', '44', '46']
    png_hex = ['89', '50', '4E', '47']
    ppt_hex = ['D0', 'CF', '11', 'E0']
    rar_hex = ['52', '61', '72', '21']
    zip_hex = ['50', '4B', '03', '04']

    L = [doc_hex, gif_hex, pdf_hex, png_hex, ppt_hex, rar_hex, zip_hex]

    if len(sys.argv) != 3:
        print ("Incorrect use of args. Run python 2 2")
        return 0

    threshold = int(sys.argv[1])
    block_size = int(sys.argv[2])

    ans = [[-1 for x in range(len(L))] for y in range(len(L))]
    cache = []
    for item in L:
        cache.append(get_first_share(item, 256, threshold, block_size))

    #find maximum n s.t all shares are distinct
    for idx1, item1 in enumerate(L):
        ret1 = cache[idx1]
        for idx2, item2 in enumerate(L):
            ret2 = cache[idx2]
            for k in range(1,256):
                if ret1[k][0] == ret2[k][0]:
                    ans[idx1][idx2] = k - 1
                    break

    #find missing shares for each header

    for idx, item in enumerate(L):
        freq = [0 for x in range(256)]
        fail = list()

        ret = cache[idx]
        for k in ret:
            if idx1 == 0:
                print(k)
            for t in k:
                freq[t] += 1

        print(freq)
        for x in range(256):
            if freq[x] == 0:
                fail.append(x)
        print(evaluate(idx), fail)

    print("Some matrix:")
    for line in ans:
        print(line)

    """
    for k in range(40,50):
        print(str(k) + " " + str(cache[-2][k]) + "-> " + str(cache[-1][k]))
    return 0
    """

if __name__ == "__main__":
    main()
