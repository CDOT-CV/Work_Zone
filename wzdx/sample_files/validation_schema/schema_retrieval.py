import json
import requests
import argparse


PROGRAM_NAME = "SchemaReferenceRetrievalTool"
PROGRAM_VERSION = "1.0"


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


def main():
    schema_url, schema_file, output_file = parse_cmd_arguments()
    if (schema_url is None) and (schema_file is None):
        raise Exception("Either schemaFile or schemaUrl must be provided")
    if schema_url is not None:
        main_schema = fetch_schema(schema_url)
    if schema_file is not None:
        main_schema = json.load(open(schema_file))
    replace_refs(main_schema)
    with open(output_file, "w") as f:
        json.dump(main_schema, f, indent=4)
        print(f"External schema references replaced and saved to {output_file}")


# parse script command line arguments
def parse_cmd_arguments():
    parser = argparse.ArgumentParser(
        description="Retrieve External Schema References - You must specify either schemaUrl or schemaFile"
    )
    parser.add_argument(
        "--version", action="version", version=f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    )
    # Current Schema URLs
    # https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/WorkZoneFeed.json
    # https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/WorkZoneFeed.json
    # https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/RoadRestrictionFeed.json
    parser.add_argument(
        "--schemaUrl",
        required=False,
        default=None,
        help="Input schema URL (for external schema reference). Must specify either schemaUrl or schemaFile",
    )
    parser.add_argument(
        "--schemaFile",
        required=False,
        default=None,
        help="Input schema file path. Must specify either schemaUrl or schemaFile",
    )
    parser.add_argument(
        "--outputFile",
        required=False,
        default="local_schema.json",
        help="Output file path",
    )

    args = parser.parse_args()
    return args.schemaUrl, args.schemaFile, args.outputFile


if __name__ == "__main__":
    main()
