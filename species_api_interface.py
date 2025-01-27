import csv
import requests

def read_queries_from_csv(input_csv):
    queries = []
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                queries.append(row[0].strip())
    return queries

def write_results_to_csv(results, output_csv):
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["query", "status", "payload"])
        for row in results:
            writer.writerow(row)

def call_swagger_api(dataset_key, queries):
    url = "https://api.gbif.org/v1/species/suggest"
    headers = {"Accept": "application/json"}
    results = []

    for q in queries:
        params = {"datasetKey": dataset_key, "q": q}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results.append([q, "Success", response.json()])
        else:
            results.append([q, "Error", response.text])

    return results

if __name__ == "__main__":
    dataset_key = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
    input_csv = "queries.csv"
    output_csv = "results.csv"
    queries = read_queries_from_csv(input_csv)
    results = call_swagger_api(dataset_key, queries)
    write_results_to_csv(results, output_csv)