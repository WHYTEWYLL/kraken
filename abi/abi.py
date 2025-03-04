#!/usr/bin/python
import argparse
import requests
import json

# Exports contract ABI in JSON

ABI_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&address=0xa59C847Bd5aC0172Ff4FE912C5d29E5A71A7512B&apikey=2BCYECR1QJHYUA4GAASKUATQDWMEPFRE37"


def __main__():

    response = requests.get(ABI_ENDPOINT)
    response_json = response.json()
    abi_json = json.loads(response_json["result"])
    result = json.dumps({"abi": abi_json}, indent=4, sort_keys=True)

    write_file = open("abi.json", "w")
    write_file.write(result)


if __name__ == "__main__":
    __main__()
