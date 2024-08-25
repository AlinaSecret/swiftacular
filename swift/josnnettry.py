import _jsonnet

def convert_jsonnet_to_json(jsonnet_snippet):
    """
    Convert a Jsonnet snippet into JSON.

    Parameters:
    - jsonnet_snippet (str): The Jsonnet code as a string.

    Returns:
    - str: The JSON output.
    """
    json_str = _jsonnet.evaluate_snippet('snippet', jsonnet_snippet)
    return json_str

jsonnet_file_path = '/home/asudakov/go/src/github.com/AlinaSecret/swiftacular/swift/deafult.jsonnet'
with open(jsonnet_file_path, 'r') as file:
    jsonnet_snippet = file.read()
json_output = convert_jsonnet_to_json(jsonnet_snippet)
print(json_output)