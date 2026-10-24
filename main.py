passages = [
    {"source" :"climate_study.pdf","page": 7,"text":"Rising temperatures can affect crop productivity"},
    {"source":"climate_study.pdf","page":8,"text":"Rainfall patterns influence yields."}
]

for passage in passages:
    print(passage["text"])
    print(f"Source: {passage['source']}, Page: {passage['page']}")
print(len(passages))
