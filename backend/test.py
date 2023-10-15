from api_reader import APIReader, Verifier
import json
from api_executor import APIExecutor
import click


# @click.option("--url", default="https://jsonplaceholder.typicode.com")
# @click.option("--url", default="https://alexwohlbruck.github.io/cat-facts/docs/")


@click.command()
def main():
    reader = APIReader()
    verifier = Verifier(reader.get_db())

    while True:
        prompt = click.prompt("What do you want to do?")

        if prompt.startswith("INGEST "):
            print("ingesting")
            _, url = prompt.split(" ")
            reader.ingest_documentation(url)
            print("done ingesting")
            continue

        for _ in range(3):
            answer, sources = verifier.verify(prompt)
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
                    api_executor = APIExecutor()
                    api_result = api_executor.execute(answer)
                    print(api_result)

                    break
                except:
                    link = reader.suggest_links(prompt)
                    reader.ingest_documentation(link)


if __name__ == "__main__":
    main()
