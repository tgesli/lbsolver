

DICT_NAME = "dictionary.txt"
OUTPUT_NAME = "lbwords.txt"

def filter_dict(input, output):
    with open(input, 'r') as infile:
        words = infile.readlines()

    lb_words = [word for word in words if  not any(word[i] == word[i+1] for i in range(len(word)-1))]

    # Write filtered words to the output file
    with open(output, 'w') as outfile:
        for word in lb_words:
            outfile.write(word)

if __name__ == '__main__':
   filter_dict(DICT_NAME, OUTPUT_NAME)