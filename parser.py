import csv

limit = 100
maxsecs = 60

def csv_writer(data, path):
    with open('output.csv', 'w') as f:
        writer = csv.writer(f)
        for line in data:
            writer.writerow(line)

if __name__ == "__main__":
    index = 0
    # newrows = [["clientid", "starttime", "endtime"]]
    newrows = []
    with open('/Users/KimMinjun/Desktop/data.csv', 'r') as f:
      reader = csv.reader(f)
      next(reader, None)

      for row in reader:
        client = int(row[0])

        timestamp = int(float(row[1]))
        lifetime = int(float(row[2]))

        newrow = [client, timestamp, lifetime]
        newrows.append(newrow)

        index += 1
        if index == limit:
            break

    lowest = 0
    highest = 0

    for row in newrows:
        timestamp = row[1]
        if timestamp < lowest or lowest == 0:
            lowest = timestamp

        if timestamp > highest or highest == 0:
            highest = timestamp

    highest = highest - lowest
    converion_rate = maxsecs / highest

    for row in newrows:
        row[1] = int((row[1] - lowest) * converion_rate)
        print(row)

    print("lowest: %d, highest: %d" % (lowest, highest - lowest))
    csv_writer(newrows, "output.csv")
