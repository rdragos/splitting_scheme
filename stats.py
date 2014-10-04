import cerealizer
import sys
import subprocess

def check_frequencies(secret, no_parties, threshold, block_size):
	sh_int = [int(str(x), 16) for x in secret]
	f = open("pdf_test.in", "wb")
	f.write(bytearray(sh_int))
	f.close()

	subprocess.call(["./main.py", str(no_parties), str(threshold), str(block_size), "pdf_test.in", "shares_dump.out"])
	allshares = cerealizer.load(open("shares_dump.out", "rb"))

	for idxShare1 in range(len(allshares)):
		sh1 = allshares[idxShare1]
		for idxShare2 in range(idxShare1 + 1, len(allshares)):
			sh2 = allshares[idxShare2]
			if sh1[0] == sh2[0]:
				return (idxShare1, idxShare2)

	return "OK"

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

	L = [pdf_hex, doc_hex, gif_hex, png_hex, ppt_hex, rar_hex, zip_hex]

	if len(sys.argv) != 4:
		print ("Incorrect use of args. Run python 256 2 2")
		return 0

	no_parties = int(sys.argv[1])
	threshold = int(sys.argv[2])
	block_size = int(sys.argv[3])

	for idx, item in enumerate(L):
		ret = check_frequencies(item, no_parties, threshold, block_size)
		print(evaluate(idx) + " " + str(ret))


	return 0

if __name__ == "__main__":
	main()

