import codecs

# http://stackoverflow.com/questions/931092/reverse-a-string-in-python
def reverse(s):
    return s[::-1]

def fix_long_line(s):
    spt = s.split(" ")
    return [reverse(" ".join(reversed(spt[:-7])))] + spt[-7:]


lines = [line.strip() for line in codecs.open("2015q1.txt", 'r', 'utf8').readlines()]

new_lines = [reverse(lines[0]).split(" "), lines[1].split(" ")]
new_lines += [fix_long_line(line) for line in lines[2:59]]
joined = ("\t".join(line) for line in new_lines)

with codecs.open("2015q1-fixed.txt", 'w', 'utf8') as f:
    f.write("\n".join(joined))