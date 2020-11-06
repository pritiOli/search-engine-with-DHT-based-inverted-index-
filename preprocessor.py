"""

Problem 2 [20 points]. Preprocess all the files using assignment #4. Save all
preprocessed documents in a single directory which will be the input to
the next assignment, index construction. Send the TA a link to a dropbox
directory where your preprocessed crawled documents are.

"""

import re
import os
import PorterStemmer
import sys

__author__ = "Priti Oli"
__email__ = "poli@memphis.edu"

# function to read and return the content of the file
# for file path passed as function parameter . catch any exception that may occur
def file_content(file_path):
    with open(file_path, 'r') as fptr:
        try:
            fileContent = fptr.read()
            return fileContent.lower() # return the file content in lower case
        except:
            return ' '

def firstLine(file_path):
    with open(file_path, 'r') as fptr:
        try:
            fline_url = fptr.readline()
            return fline_url.lower() # return the file content in lower case
        except:
            return ' '

current_dir = os.getcwd() # variable to get the path of current working directory
sys.path.append(current_dir) # set the current path in the system variable
list_stopword = file_content(os.path.join(current_dir, 'english_stopwords.txt')) # varible that contains all the stop word as str
stopword_list = list_stopword.split() # list of stop word
word_pattern = re.compile("[A-Za-z]") # word pattern to match word only

# funtion to remove stopword from the given content
def remove_stopWords(content):
    global  current_dir,stopword_list
    new_text = " "
    word_list = str(content).split()
    for word in word_list:
        # if the current exists in stop word list filter out the word
        if word not in stopword_list:
            new_text = new_text+word+"  "
    return new_text

# function to remove punctuations from the given content
def remove_punctuations(content):
    content = str(content)
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    # loop for each symbol and remove each symbol from the content
    for symbol in symbols:
        content = content.replace(symbol,' ')
    return content

# function to convert the given content in lower case format
def convert_lowerCase(content):
    return str(content).lower()

# function to strip HTML by matching regex
def strip_HTML(content):
    return re.sub(r'<[^>]*?>', ' ', str(content))

# funtion to substitue numeric value from content by matching regex
def removeNumber(content):
    return re.sub(r'\b\d+(?:\.\d+)?\s+', ' ', content)

# function to implement stemming by using porterstemmer module linked in the course website
def stemmingOfWords(content):
    #     use portor stemmer
    p = PorterStemmer.PorterStemmer()
    word = ' '
    stemmed_text = " "
    for word in content:
        stemmed_word = p.stem(word, 0, len(word) - 1).lower()
        stemmed_text = stemmed_text+stemmed_word
    return stemmed_text

def remove_javascript(text):
    scripts = re.compile(r'<(script).*?</\1>(?s)')
    css = re.compile(r'<style.*?/style>')
    tags = re.compile(r'<.*?>')

    text = scripts.sub('', text)
    text = css.sub('', text)
    text = tags.sub('', text)
    return text


# function to preprocess the file content
def preprocess(file_content):
    processed_content = convert_lowerCase(file_content)
    processed_content = remove_javascript(processed_content)
    processed_content = strip_HTML(processed_content)
    processed_content = removeNumber(processed_content)
    processed_content = remove_punctuations(processed_content)
    processed_content = remove_stopWords(processed_content)
    processed_content = stemmingOfWords(processed_content)
    return  processed_content

# function to output the preprocessed file in output directory
def file_ouput(file, content,url):
    global  current_dir
    output_dir = os.path.join(current_dir, 'preprocessed_output')
    output_file = os.path.join(output_dir,file)
    try:
        with open(output_file, 'w+') as fp:
            fp.write(url+" \n \n ")
            fp.write(content)
            print(" Output copied in the  output directory "+file)
    except IOError:
        print(" an exception occured while writing to  "+file)

# main functions
def main():
    global current_dir
    input_dir = os.path.join(current_dir, 'raw_files')
    print(' input directory '+input_dir)
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file);
        processed_content = preprocess(file_content(file_path))
        file_ouput(file, processed_content,firstLine(file_path))

if __name__ == '__main__':
    main()