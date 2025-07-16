import glob

path = "/data/shape-impulse/*"

folders = glob.glob(path)

# print(folders)
dataset = {}

for folder in folders:
    files = glob.glob(folder + "/bowl_shapenet/csv/*")
    for file in files:
        data = file.split("/")[-1].split(".")[0].split("-")
        if data[0] in dataset:
            dataset[data[0]].append(int(data[1]))
        else:
            dataset[data[0]] = [int(data[1])]

minValue = 30000
maxValue = 0
for data in dataset:
    print(data, dataset[data])
    print(max(dataset[data]), len(dataset[data]))

    if len(dataset[data]) < minValue:
        minValue = len(dataset[data])
    if len(dataset[data]) > maxValue:
        maxValue = len(dataset[data])

print(minValue, maxValue)

    # print(len(values))