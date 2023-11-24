import logging, time
import pandas as pd
import openpyxl as xl
import pyexcel as p
from constants import MongoDB_URL, path, product_list_path, dest_overview, dest_product,dest_standalone, dest_support, end_user
import logging
import json
from conftest import services_context_manager
from utils import (
    get_modified_payload,
    watch_RabbitMQ_tester_consume,
    watch_RabbitMQ_tester_publish,
    watch_mongoDB_Discovery,connect_azure_storage_account, 
    get_list_of_blob, 
    create_local_sheet_delete_unwanted_rows_cols, 
    watch_mongoDB, download_blob, upload_blob_file, 
    delete_blob
)
import requests


def test_AAS_Success_Case():
    global source_id
    with services_context_manager("test_AAS_Success_Case"):
        source_id = get_modified_payload("action", "Activate")
        logging.info(f"Source ID is {source_id}")
        with open("modified_json.json", "r") as f:
            publish_payload = json.load(f)
        publish_payload = json.dumps(publish_payload)
        watch_RabbitMQ_tester_publish(publish_payload)
        aas_response = watch_RabbitMQ_tester_consume(source_id)
        logging.info(f"AAS response is {aas_response}")
        assert aas_response == "Success"
        logging.info("Successfully received data in consume queue.")
        db_doc = watch_mongoDB(MongoDB_URL, source_id)
        assert db_doc != None
        assert db_doc['g_active']
        assert db_doc['activation_action'] == "Activate"
        assert db_doc['g_last_action'] == "Activate"
        assert db_doc['g_last_actioned_on']
        assert db_doc['g_created_on']


def test_AAS_Failure_Case():
    with services_context_manager("test_AAS_Failure_Case"):
        source_id = get_modified_payload("action", "activate")
        logging.info(f"Source ID is {source_id}")
        with open("modified_json.json", "r") as f:
            publish_payload = json.load(f)
        publish_payload = json.dumps(publish_payload)
        watch_RabbitMQ_tester_publish(publish_payload)
        aas_response = watch_RabbitMQ_tester_consume(source_id)
        logging.info(f"AAS response is {aas_response}")
        assert aas_response == "Failure"
        logging.info("Successfully received data in consume queue.")
  

def test_Discovery_Success_case():
    logging.info("Start for Success cases of POC_Discovery")
    #connect to azure storage account
    blob_service_client = connect_azure_storage_account()
    upload_blob_file(blob_service_client)
    get_list_of_blob(blob_service_client)
    # download_blob(blob_service_client)
    create_local_sheet_delete_unwanted_rows_cols(path,dest_overview, "Overview")
    create_local_sheet_delete_unwanted_rows_cols(path,dest_standalone,"Standalone")
    #reads the first sheet of your local overview sheet and flter out based on enduser.
    df = pd.read_excel(dest_overview, sheet_name='NewSheet') 
    df = df[(df['End User']==end_user)]
    assert not df.empty
    list_overview = df.values.tolist()
    logging.info(f'SO# for the enduser - {list_overview[0][1]}')
    #reads the first sheet of local standalone file and get the sku id's for respective "SO#".
    df = pd.read_excel(dest_standalone, sheet_name='NewSheet') 
    df = df[(df['SO#']==list_overview[0][1])]
    assert not df.empty
    list_product = df.values.tolist()
    logging.info(f'From Standalone sheet- {list_product}')
    sku_id = list_product[1][2]
    logging.info(f"The SKU id is -{sku_id}")
    #get the prodict details for respective skuid's from product list sheet
    df = pd.read_excel(product_list_path, sheet_name='Upload list') #reads the product_list
    df = df[(df['Part Number ']==sku_id)]
    assert not df.empty
    product_list_data = df.values.tolist()
    logging.info(f'Product complete data from Product List sheet- {product_list_data}')
    time.sleep(25)
    MongoDB_Data = watch_mongoDB_Discovery(MongoDB_URL,'CPSB-NGTP-5600-2Y-HA')
    logging.info(f'Data from MongoDB-{MongoDB_Data}')
    assert MongoDB_Data != None, "MongoDB data is empty."
    assert product_list_data[0][1] == MongoDB_Data['skuId']
    assert product_list_data[0][5] == MongoDB_Data['licenseName']
    assert product_list_data[0][0] == MongoDB_Data['category']
    assert MongoDB_Data['gUploadedOn']
    logging.info(f'gUploadId is : {MongoDB_Data["gUploadId"]}')
    logging.info(f'gUploadedOn date is : {MongoDB_Data["gUploadedOn"]}')
    delete_blob(blob_service_client)
    logging.info("End of Success cases of POC_Discovery")

    
