# Schemas

This directory holds WZDx schemas for use in validation of generated messages, as well as a tool to resolve external schema references.

## Work Zone Feed

WZDx feed schemas, pulled directly from the USDOT repository:

[WZDx 4.2 Schema](https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/WorkZoneFeed.json)

[WZDx 4.1 Schema](https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.1/WorkZoneFeed.json)

## Road Restriction Feed

WZDx Road Restriction feed schemas, pulled directly from the USDOT repository:

[Road Restriction Feed 4.0](https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/RoadRestrictionFeed.json)

## Generating Local Schemas

jsonschema is moving towards a system not allowing default external schema references. The best solution to this is to pull all external schemas into local schema files. This can be completed manually, or by running the schema_retrieval script:

### External Schema URL

```sh
python ./schema_retrieval.py --schemaUrl "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.2/WorkZoneFeed.json" --outputFile ./work_zone_feed_v42_dereferenced.json
```

### Local Schema File

```sh
python ./schema_retrieval.py --schemaFile ./work_zone_feed_v42.json --outputFile ./work_zone_feed_v42_dereferenced.json
```
