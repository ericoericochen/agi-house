import requests


class APIExecutor:
    def execute(self, api_params: dict):
        method = api_params["method"]
        url = api_params["url"]
        headers = api_params.get("headers", {})

        if method == "GET":
            res = requests.get(url, headers=headers)
        elif method == "POST":
            res = requests.post(url, headers=headers)
        elif method == "PUT":
            res = requests.put(url, headers=headers)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers)
        elif method == "PATCH":
            res = requests.patch(url, headers=headers)

        return res.text


if __name__ == "__main__":
    executor = APIExecutor()

    res = executor.execute(
        {
            "method": "GET",
            "url": "https://jsonplaceholder.typicode.com/posts",
        }
    )

    print(res)
