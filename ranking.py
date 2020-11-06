import pickle
import math

similarity_dict = {}

def rank_docs():
    # global similarity_dict
    return similarity_dict


def __query(word,lookupVal):
    # with open('inverted_index.pickle', 'rb') as inverted_index:
    #      indexes = pickle.load(inverted_index)
    # keys = indexes.keys()
    # if not word in keys:
    #          return " sorry no result found "
    document_frequency = len(lookupVal)
    max_frequency=0
    for values in lookupVal:
        # print(type(values))
        if not type(values) is list:
            continue
        if (max_frequency < int(values[1])):
            max_frequency = int(values[1])
    #
    for values in lookupVal:  # checking word in the dictionary
        if not type(values) is list:
            continue
        cosine_similarity(values, max_frequency, document_frequency)


def cosine_similarity(value, max_frequency, document_frequency):
    global similarity_dict

    # with open('document_length.pickle','rb') as handle2:
    #     c = pickle.load(handle2)
    document_length = 100

    # key = 'output\\'+value[0]
    collection_length = 100


    # print(max_frequency)
    tf_frequency = int(value[1])/int(max_frequency)

    total_documents = 10000
    idf = math.log(total_documents/document_frequency)


    query_length = 1

    similarity = (tf_frequency*idf)/(collection_length*query_length)

    check_document = value[0]
    if (str(check_document) in similarity_dict.keys()):
        similarity_dict[check_document] = similarity_dict[check_document]+similarity
    else:
        similarity_dict[check_document]= similarity
    return

