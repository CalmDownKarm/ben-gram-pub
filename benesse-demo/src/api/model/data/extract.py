file = open('test.m2')

lis = file.readlines()
lis = [i.strip() for i in lis]

for line in lis:
	if(line.startswith('S')):
		print(" ".join(line.split()[1:]))
