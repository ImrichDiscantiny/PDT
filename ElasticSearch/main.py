import os
import json

from elasticsearch import Elasticsearch, helpers
from pympler import asizeof



def parse_format_json(): 

    f = open("repositories.json", encoding="utf8", errors='ignore')
    faw = open("parsed_repositories.json", 'w')

    for line in f: # read line by line

        record = json.loads(line.replace('\\\\', '\\'))
        json.dump(record, faw)
        faw.write('\n')
        

def bulk_import():

    es = Elasticsearch(['http://localhost:9200'], headers={'Content-Type': 'application/x-ndjson'},request_timeout=120)
    lines = []
   
    f = open("parsed_repositories.json", encoding="utf8", errors='ignore')
    
    if  os.path.isfile("index_buffer.json"):
        fbuf = open("index_buffer.json", "r")
        index = json.load(fbuf)['buffer']
        
        fbuf.close()
        print(index)
    else:
        index = 0
  

    for line in f: # read line by line
        lines.append(line)

    llen = len(lines)
    bytelen = 0
    bulk_insert = ''
    
    while index < llen + 1:

        if  bytelen < 67 and index != llen:

            l = json.loads(lines[index])
        
            print(index, ': ',asizeof.asizeof( l)/ 1024 / 1024) # velkost v mega bajtoch
        
            bytelen = bytelen + (asizeof.asizeof( l)/ 1024 / 1024) # celkova velkost v mega bajtoch

            action = {"create": {"_id": str(index)}}
            
            bulk_insert = bulk_insert + json.dumps(action) + "\n" + json.dumps(l) + "\n"

            index = index + 1   
        
        elif bytelen >= 67 or index == llen:  # primeraj podla potreby
            print("Sending data... ", bytelen)
            res = es.bulk(operations=bulk_insert, index='repositories')
            
            print(res)
            bulk_insert = ""
            bytelen = 0

            fbuf = open("index_buffer.json", "w")
            json.dump({"buffer": index}, fbuf)
            fbuf.close()

      
    
    f.close()
    return

if __name__ == "__main__":

    i = input("1 - requests, 2 -  parse: ")

    if i == "1":
        bulk_import()
    else:
        parse_format_json()