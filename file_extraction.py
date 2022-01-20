import glob

data = []
print("The names of files in the lfw are:")
for i in glob.glob("/home/userone/Downloads/lfw/**/*"):
    print(i)
    data.append(i)
    import os
    name = os.path.basename(i)
    print(name)

print(len(data))
