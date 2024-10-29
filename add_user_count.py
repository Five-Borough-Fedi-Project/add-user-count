import argparse
import csv
import requests
import socket
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="Find active users for a CSV of fedi servers.",
    description="Takes an input CSV from the Mastodon moderation page and adds active user counts to it in a new file.",
)

parser.add_argument("filename")
args = parser.parse_args()
csv_input = Path(args.filename)
csv_output = Path(args.filename + ".USERCOUNTS.csv")
if not csv_input.is_file():
    raise FileNotFoundError(f"File not found: {csv_input}")

ni_path = "/nodeinfo/2.0"
headers = {"Accept": "application/json"}

print("Will write to " + str(csv_output))


def resolve_server(server):
    try:
        return socket.gethostbyname(server)
    except:
        return None


def active_user_count(server):
    if not resolve_server(server):
        return -1
    else:
        try:
            r = requests.get("https://" + server + ni_path, headers=headers, timeout=5)
            r.raise_for_status()
            response = r.json()
        except:
            return -1
        return response.get("usage", {}).get("users", {}).get("total", -1)


def process():
    results = []
    with open(csv_input, newline="") as csv_in_open:
        spamreader = csv.reader(csv_in_open)  # , delimiter=" ", quotechar="|")
        for row in spamreader:
            auc = active_user_count(row[0])
            results.append([row[0], auc])
            print(f"{row[0]}: {auc}")

    with open(csv_output, "w", newline="") as csv_out_open:
        spamwriter = csv.writer(csv_out_open)
        for result in results:
            spamwriter.writerow(result)


if __name__ == "__main__":
    process()
