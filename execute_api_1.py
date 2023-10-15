from api_reader import APIReader, Verifier
import json
from api_executor import APIExecutor
import click


def create_api_reader():
    reader = APIReader(
        "https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/reference/ASLR_cmds.html"
    )
    verifier = Verifier(reader.get_db())

    return verifier


def run_inference(prompt: str, reader, ver0          ifier):
    if prompt.startswith("INGEST "):
        print("ingesting")
        _, url = prompt.split(" ")
        reader.ingest_documentation(url)
        print("done ingesting")

        return {}

    for _ in range(3):
        try:
            answer, sources = verifier.verify(prompt)
            print(sources)
            # parse only the dict struct inside the string; may contain text surrounding it
            answer = answer[answer.find("{") : answer.rfind("}") + 1]

            answer = json.loads(answer)
        except:
            continue
        if answer["failure_and_suggestions"] == "CANNOT DO":
            link = reader.suggest_links(prompt)
            reader.ingest_documentation(link)
        else:
            try:
                api_executor = APIExecutor()
                api_result = api_executor.execute(answer)
                print(api_result)

                return api_result

            except:
                link = reader.suggest_links(prompt)
                reader.ingest_documentation(link)
