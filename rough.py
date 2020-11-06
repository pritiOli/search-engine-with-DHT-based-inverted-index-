import pickle
import nltk
words = set(nltk.corpus.words.words())

words = ['donald','trump','nepal','kathmandu','covid-19','2020','corona','virus','london','UK','USA','turkey','peru',
         'machu','pichu','france','paris','england','switzerland','rome','italy','hurricane','memphis','nashville'
         'Apple','stock','India','unemployed','lock','down','china','germany','sweden','canada','mexico',
         'joe','biden','presidential','president','debate','kamala','harris','russia','vaccine','bat','election',
         'win','remote','new','normal','working','work','from','home','black','lives','matter','all','fake','news',
         'olympics','europe','travel','restriction','alaska','camnudge','holiday','online','sale','season','flu',
         'isolation','quarantine','novel','headache','flu','pneumonia','diarrhea','vomiting','Italy','death',
         'infected','protest','campaign','equality','japan','ireland','tennessee','mississippi','cruise','herd',
         'immunity','climate','change','dr','fauci','world','health','organization']
file= open('inverted_index.pickle','rb')
data=pickle.load(file)
file.close()
keys = data.keys()
print(len(keys))
clean_dict={}
for key in keys:
    if(key.lower() in words and key.isalpha()):
        clean_dict[key]=data[key]
with open('index.pickle', 'wb') as handle:
    pickle.dump(clean_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
file1= open('index.pickle','rb')
data1=pickle.load(file1)
keys1 = data1.keys()
print(len(keys1))
for key in keys1:
    print(key)