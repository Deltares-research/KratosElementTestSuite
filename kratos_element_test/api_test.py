import requests


if __name__ == "__main__":
    data_uri = "https://geolab-test.avi.directory.intra/api/GeoData"

    results_uri = requests.get(data_uri, verify=False)
    print(f"status code = {results_uri.status_code}")
    results = results_uri.json()

    print(results)