import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from requests import get, post, patch, delete

load_dotenv()


def parse_configuration():
    path = Path.cwd() / "labels.yml"
    contents = path.read_text("utf-8")
    parsed: dict[str, dict] = yaml.safe_load(contents)

    owners = {}
    updates = {}
    labels = {}

    for operation, data in parsed.items():
        for value in data:
            if operation == "owners":
                owner = str(value.get("name", ""))
                is_org = bool(value.get("is_org", True))
                token = str(value.get("token", ""))

                if len(token) == 0:
                    sys.exit(f"Token of owner {owner} is empty!")

                owners[owner] = {
                    "is_org": is_org,
                    "token": str(os.environ.get(token, ""))
                }
            elif operation == "updates":
                current = str(value.get("current", ""))
                target = str(value.get("target", ""))
                delete = bool(value.get("delete", False))

                updates[current] = {
                    "current": current,
                    "target": target,
                    "delete": delete
                }
            elif operation == "custom":
                name = str(value.get("name", ""))
                description = str(value.get("description", ""))
                color = str(value.get("color", "ffffff")).lower()

                labels[name] = {
                    "name": name,
                    "description": description,
                    "color": color
                }

    return owners, updates, labels


HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Lemon's Label Editor (+https://github.com/justalemon/.github/blob/master/labels.yml)",
    "X-GitHub-Api-Version": "2022-11-28"
}
OWNERS, UPDATES, LABELS = parse_configuration()


def get_headers(token: str):
    headers = dict(HEADERS)
    headers["Authorization"] = f"Bearer {token}"
    return headers


def format_labels(labels: list[dict]):
    new_labels = {}

    for label_data in labels:
        name = label_data["name"]
        new_labels[name] = label_data

    return new_labels


def get_labels_for_slug(token: str, slug: str):
    url = f"https://api.github.com/repos/{slug}/labels?per_page=100"
    resp = get(url, headers=get_headers(token))
    resp.raise_for_status()
    return format_labels(resp.json())


def process_labels_for_repo(token: str, slug: str):
    print(f"Started processing repo {slug}")

    labels = get_labels_for_slug(token, slug)

    for name, existing_label in labels.items():
        if name not in UPDATES:
            continue

        update = UPDATES[name]

        if update["delete"]:
            delete(existing_label["url"], headers=get_headers(token)).raise_for_status()
            print(f"Deleted label {name} in {slug}")
            continue
        else:
            replacement = LABELS[update["target"]]
            new_name = replacement["name"]
            patch_data = {
                "new_name": new_name,
                "color": replacement["color"],
                "description": replacement["description"]
            }
            patch(existing_label["url"], json=patch_data, headers=get_headers(token)).raise_for_status()
            print(f"Replaced {name} with {new_name} in {slug}")

    labels = get_labels_for_slug(token, slug)

    for name, new_label in LABELS.items():
        if name in labels:
            existing_label = labels[name]

            if existing_label["description"] != new_label["description"] or existing_label["color"] != new_label["color"]:
                patch_data = {
                    "color": new_label["color"],
                    "description": new_label["description"]
                }
                patch(existing_label["url"], json=patch_data, headers=get_headers(token)).raise_for_status()
                print(f"Update description and/or color of {name} in {slug}")
        else:
            post(f"https://api.github.com/repos/{slug}/labels", json=new_label, headers=get_headers(token)).raise_for_status()
            print(f"Created {name} in {slug}")

    print(f"Finished processing repo {slug}")


def process_repos_from_owner(token: str, owner: str, is_org: bool):
    print(f"Processing repos owned by {owner}")

    page = 1
    repos = []

    while True:
        print(f"Fetching page {page} of {owner}")

        endpoint = "orgs" if is_org else "users"
        url = f"https://api.github.com/{endpoint}/{owner}/repos?per_page=100&page={page}"

        resp = get(url, headers=get_headers(token))
        resp.raise_for_status()

        new_repos = resp.json()

        if not new_repos:
            print(f"Page {page} is empty!")
            break

        repos.extend(new_repos)
        page += 1

    for repo in repos:
        slug = repo["full_name"]

        if repo["archived"]:
            print(f"Skipping {slug} because is archived")
            continue

        if repo["fork"]:
            print(f"Skipping {slug} because is a fork")
            continue

        process_labels_for_repo(token, slug)


def main():
    for owner, info in OWNERS.items():
        process_repos_from_owner(info["token"], owner, info["is_org"])

    print("Done!")


if __name__ == "__main__":
    main()
