import urllib.request

lines = (line.strip().split(" ") for line in open("download.txt"))
for line in lines:
    s = line[0]
    print(s)
    ext  = s[s.rfind(".")+1:]
    urllib.request.urlretrieve(line[0], line[1] + "." + ext)
