from api_reader import APIReader, Verifier
import json
from api_executor import APIExecutor
import click


def create_api_reader():
    pass


reader = APIReader()


def run_inference(
    prompt: str,
    verifier=Verifier(reader.get_db()),
):
    if prompt.startswith("INGEST "):
        print("ingesting")
        _, url = prompt.split(" ")
        reader.ingest_documentation(url)
        print("done ingesting")
        return {"Success": True}

    for _ in range(3):
        if prompt.startswith("API"):
            answer, sources = verifier.verify(prompt)
        else:
            title_prompt = (
                "Write AppleScript code that does the following tasks:" + prompt
            )
            answer, sources = verifier.verify(title_prompt)

        print(answer)
        # parse only the dict struct inside the string; may contain text surrounding it
        answer = answer[answer.find("{") : answer.rfind("}") + 1]
        answer = json.loads(answer)
        if answer["failure_and_suggestions"] == "CANNOT DO":
            link = reader.suggest_links(prompt)
            reader.ingest_documentation(link)
        else:
            try:
                print(answer)
                print("---")
                print(sources)
                if prompt.startswith("API"):
                    api_executor = APIExecutor()
                    api_result = api_executor.execute(answer)
                    print(api_result)

                    return api_result

                return api_result["code"]
            except:
                link = reader.suggest_links(prompt)
                reader.ingest_documentation(link)
