import sys
import os
import time
import yaml
import json
import csv
import urllib3
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import SubscriptionClient


def config():
    with open('config.yml', 'r') as config_settings:
        config_info = yaml.safe_load(config_settings)
        username = str(config_info['defaults']['username']).rstrip()
        password = str(config_info['defaults']['password']).rstrip()
        URL = str(config_info['defaults']['apiURL']).rstrip()
        debug = config_info['defaults']['debug']
        csa = config_info['defaults']['csa']
        if username == '' or password == '' or URL == '':
            print(
                "Config information in ./config.yml not configured correctly. Exiting...")
            sys.exit(1)
    return username, password, URL, debug, csa


def Post_Call(username, password, URL, data_connector):

    usrPass = str(username)+':'+str(password)
    headers = urllib3.make_headers(basic_auth=usrPass)
    headers['X-Requested-With'] = "Qualys (python)"
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'
    http = urllib3.PoolManager()
    r = http.request('POST', URL, body=data_connector, headers=headers)
    # r = requests.post(URL, body=data_connector, headers=headers)
    return r.status


def Add_AZURE_Connector():
    username, password, URL, debug, csa = config()
    URL = URL + "/qps/rest/3.0/create/am/azureassetdataconnector"

    if debug:
        print(
            '------------------------------AZURE Connectors--------------------------------')
        if not os.path.exists("debug"):
            os.makedirs("debug")
        debug_file_name = "debug/debug_file" + \
            time.strftime("%Y%m%d-%H%M%S") + ".txt"
        debug_file = open(debug_file_name, "w")
        debug_file.write(
            '------------------------------AZURE Connectors--------------------------------' + '\n')
    # df = pd.read_excel('AZURE_CONNECTOR_INFO.xlsx', sheet_name='Sheet1')
    with open('AZURE_CONNECTOR_INFO.csv', 'r') as f:
        reader = csv.DictReader(f)
        a = list(reader)
        f.close()
    counter = 0
    for i in a:
        counter += 1
        AppID = i['APPLICATIONID']
        AzureAuthKeyID = i['AUTHKEY']
        SubID = i['SUBSCRIPTIONID']
        DirectoryID = i['DIRECTORYID']
        DESC = i['DESC']
        NAME = i['NAME']
        from azure.common.credentials import ServicePrincipalCredentials


        # Specify your Azure credentials


        # Authenticate with Azure using Service Principal credentials
        credentials = ServicePrincipalCredentials(
            client_id=str(AppID), secret=str(AzureAuthKeyID), tenant=str(DirectoryID))

        # Create a SubscriptionClient to interact with subscriptions
        subscription_client = SubscriptionClient(credentials)

        # Use the SubscriptionClient to get the subscription by ID
        subscription = subscription_client.subscriptions.get(str(SubID))

        # Print the name of the subscription
        sub_name = subscription.display_name

        if debug:
            print(str(counter) + ' : AZURE Connector')

            debug_file.write(str(counter) + ' : AZURE Connector' + '\n')

            debug_file.write('---' + 'NAME : ' + str(NAME) + '\n')
            debug_file.write('---' + 'DESC : ' + str(DESC) + '\n')
            debug_file.write('---' + 'Application ID : ' + str(AppID) + '\n')
            debug_file.write('---' + 'Subscription ID : ' + str(SubID) + '\n')
            debug_file.write('---' + 'Directory ID : ' +
                             str(DirectoryID) + '\n')
        av_data = {
            "ServiceRequest": {
                "data": {
                    "AzureAssetDataConnector": {
                        "name": "{}".format(sub_name),
                        "description": "Azure connector created using API",


                        "disabled": 'false',
                        "runFrequency": 240,
                        "isRemediationEnabled": 'true',
                        "isGovCloudConfigured": 'false',
                        "authRecord": {
                            "applicationId": "{}".format(str(AppID)),
                            "directoryId": "{}".format(str(DirectoryID)),
                            "subscriptionId": "{}".format(str(SubID)),
                            "authenticationKey": "{}".format(str(AzureAuthKeyID))
                        },
                        "connectorAppInfos": {
                            "set": {
                                "ConnectorAppInfoQList": [
                                    {
                                        "set": {
                                            "ConnectorAppInfo": {
                                                "name": "AI",
                                                "identifier": "{}".format(str(SubID))
                                            }
                                        }
                                    }

                                ]
                            }
                        }
                    }
                }
            }
        }
        av_encoded_data = json.dumps(av_data).encode('utf-8')
        csa_data = {
            "ServiceRequest": {
                "data": {
                    "AzureAssetDataConnector": {
                        "name": "{}".format(sub_name),
                        "description": "Azure connector created using API",


                        "disabled": 'false',
                        "runFrequency": 240,
                        "isRemediationEnabled": 'true',
                        "isGovCloudConfigured": 'false',
                        "authRecord": {
                            "applicationId": "{}".format(str(AppID)),
                            "directoryId": "{}".format(str(DirectoryID)),
                            "subscriptionId": "{}".format(str(SubID)),
                            "authenticationKey": "{}".format(str(AzureAuthKeyID))
                        },
                        "connectorAppInfos": {
                            "set": {
                                "ConnectorAppInfoQList": [
                                    {
                                        "set": {
                                            "ConnectorAppInfo": {
                                                "name": "AI",
                                                "identifier": "{}".format(str(SubID))
                                            }
                                        }
                                    },
                                    {
                                        "set": {
                                            "ConnectorAppInfo": {
                                                "name": "CI",
                                                "identifier": "{}".format(str(SubID))
                                            }
                                        }
                                    },
                                    {
                                        "set": {
                                            "ConnectorAppInfo": {
                                                "name": "CSA",
                                                "identifier": "{}".format(str(SubID))
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        csa_encoded_data = json.dumps(csa_data).encode('utf-8')

        try:
            if csa:
                Post_Call(username, password, URL, csa_encoded_data)
            else:
                Post_Call(username, password, URL, av_encoded_data)
            if debug:
                print(str(counter) + ' : Connector Added Successfully')
                print('-------------------------------------------------------------')
                debug_file.write(
                    str(counter) + ' : Connector Added Successfully' + '\n')

        except Exception as e:  # This is the correct syntax
            print(str(counter) + ' : Failed to Add Azure Connector')
            print(e)
            print('-------------------------------------------------------------')
            if debug:
                debug_file.write(
                    str(counter) + ' : Failed to Add Azure Connector' + '\n')
                debug_file.write(str(e) + '\n')
    if debug:
        debug_file.close()


Add_AZURE_Connector()
