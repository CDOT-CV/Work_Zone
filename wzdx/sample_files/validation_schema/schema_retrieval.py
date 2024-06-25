import json
import requests


def fetch_schema(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch schema from {url}")


def replace_refs(schema, base_url=""):
    if isinstance(schema, dict):
        # Handle $ref in objects
        if (
            "$ref" in schema
            and isinstance(schema["$ref"], str)
            and schema["$ref"].startswith("http")
        ):
            external_schema = fetch_schema(schema["$ref"])
            # Remove the $ref key after fetching the external schema
            del schema["$ref"]
            # Update the schema with the fetched external schema
            schema.update(external_schema)
            replace_refs(schema, base_url)
        else:
            # Recursively replace refs in dictionary items
            for key, value in schema.items():
                replace_refs(value, base_url)
    elif isinstance(schema, list):
        # Recursively replace refs in list items
        for item in schema:
            replace_refs(item, base_url)


def main(schema_url):
    main_schema = fetch_schema(schema_url)
    replace_refs(main_schema)
    with open("local_schema.json", "w") as f:
        json.dump(main_schema, f, indent=4)


# Example usage
# https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/WorkZoneFeed.json
# https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/WorkZoneFeed.json
# https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/RoadRestrictionFeed.json
schema_url = "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/RoadRestrictionFeed.json"
main(schema_url)
