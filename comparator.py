def count_matching_lines(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        # Skip the first two lines of each file
        for _ in range(2):
            next(f1)
            next(f2)

        # Store the remaining lines in sets
        lines_f1 = set(line.strip() for line in f1)
        lines_f2 = set(line.strip() for line in f2)

    # Calculate the intersection of the sets
    matching_lines = lines_f1.intersection(lines_f2)

    return len(matching_lines), len(lines_f1), len(lines_f2)


if __name__ == "__main__":

    file1 = input('Input the filename of your file : ')
    file2 = input('Input the filename of the provided file : ')
    matching_lines_count, total_lines_f1, total_lines_f2 = count_matching_lines(
        file1, file2)
    print(f"The number of matching lines is: {matching_lines_count}")
    print(f"Total number of lines in {file1}: {total_lines_f1}")
    print(f"Total number of lines in {file2}: {total_lines_f2}")
    print(f"Ratio: {matching_lines_count/float(total_lines_f2)*100}%")
