# Monitoring Resources

## Experimental Monitoring Cloud Function

This folder contains a cloud function which diffs the production and experimental wzdx REST feeds. The outputs of this cloud function are the full production feed response (/prod), the full experimental feed response (/experimental), and the differences (/diff), are all separately stored in a GCP bucket. Each subdirectory is delineated by year, month, and day, and each file is named by timestamp, like 20240631-152432.json
