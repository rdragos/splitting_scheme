import cerealizer
import sys

def main():
    allshares = cerealizer.load(open(sys.argv[1], "rb"))
    print(allshares)

if __name__ == "__main__":
    main()
