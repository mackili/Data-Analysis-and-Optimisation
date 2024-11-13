import json
import xmltodict

# open the netex_oebb_InfrastructureNetwork_20231211 xml file and parse it to JSON
with open(
    "NetEx/ÖBB NetEx files/netex_oebb_InfrastructureNetwork_20231211.xml"
) as xml_file:

    data_dict = xmltodict.parse(xml_file.read())
    # xml_file.close()

    # generate the object using json.dumps()
    # corresponding to json data

    json_data = json.dumps(data_dict)

    # Write the json data to output
    # json file
    with open("NetEx/netex_oebb_InfrastructureNetwork.json", "w") as json_file:
        json_file.write(json_data)
        # json_file.close()

# open the netex_oebb_InfrastructureNetwork_20231211 xml file and parse it to JSON

with open("NetEx/ÖBB NetEx files/netex_oebb_StoppPlaces_20231211.xml") as xml_file:

    data_dict = xmltodict.parse(xml_file.read())
    # xml_file.close()

    # generate the object using json.dumps()
    # corresponding to json data

    json_data = json.dumps(data_dict)

    # Write the json data to output
    # json file
    with open("NetEx/netex_oebb_StoppPlaces.json", "w") as json_file:
        json_file.write(json_data)
        # json_file.close()
