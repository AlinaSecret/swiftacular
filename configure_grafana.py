from grafana_client import GrafanaApi
import json

# Configuration
grafana_url = "192.168.100.150:3000"
username = "admin"
password = "admin"

# Initialize the Grafana API client
client = GrafanaApi(auth=(username, password), host=grafana_url)

# Datasource configuration
datasource_config = {
    "name":"swift-storage-01",
    "type":"pcp-redis-datasource",
    "url":"http://192.168.100.201:44322",
    "access":"proxy",
    "basicAuth":False,
    "isDefault":False,
    "editable":True
}

# Create datasource
def create_datasource():
    try:
        client.datasource.create_datasource(datasource_config)
        print("Datasource created successfully")
    except Exception as e:
        print(f"Failed to create datasource: {e}")

# Create datasource
def delete_datasource():
    try:
        client.datasource.delete_datasource_by_name("PCP Redis")
        print("Datasource deleted successfully")
    except Exception as e:
        print(f"Failed to delete datasource: {e}")

# Read dashboard JSON from file
def read_dashboard_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            dashboard_json = json.load(file)
        return dashboard_json
    except Exception as e:
        print(f"Failed to read dashboard file: {e}")
        return None

# Create dashboard
def create_dashboard(dashboard_json):
    try:
        response = client.dashboard.update_dashboard({
            "dashboard": dashboard_json,
            "overwrite": True,
           "message": "g"
        })
        print(response)
        print("Dashboard created successfully, ID:", response["id"])
    except Exception as e:
        print(f"Failed to create dashboard: {e}")

# create-pcp-datasource endpoint user password name ip
# delete-default-pcp-datasource endpoint user password
# create-dashboard endpoint user password json_file_path  -> return in stdout response[url]

if __name__ == "__main__":
    create_datasource()
    delete_datasource()
    create_dashboard(read_dashboard_from_file("/home/asudakov/go/src/github.com/AlinaSecret/swiftacular/host_overview_dashboard.json"))