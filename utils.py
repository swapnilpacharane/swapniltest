import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import openpyxl as xl
import pandas as pd
import pymongo
import os
import random, string, json, pika, ssl
from random import randint

from constants import publish_queue_tester, consume_queue_tester, username, password, host, virtual_host, aas_exchange, connect_str, container_name


def connect_azure_storage_account():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    logging.info(blob_service_client)
    return blob_service_client
    
def get_list_of_blob(blob_client):    
    container_client = blob_client.get_container_client(container=container_name)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        logging.info(f"Name: {blob.name}")
    
def download_blob(blob_client):
    blob_client = blob_client.get_blob_client(container=container_name, blob="Exported_Orders_7.xls")
    with open(file=os.path.join(r'C:\Users\sachin12.patel\Downloads', 'check.xls'), mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())   
       
def upload_blob_file(blob_client):
    global random_number
    random_number = "".join([str(randint(0, 9)) for i in range(2)])
    container_client = blob_client.get_container_client(container=container_name)
    with open(file=os.path.join(os.getcwd(), 'Exported Orders - 1992.xls'), mode="rb") as data:
        blob_client = container_client.upload_blob(name="Exported_Orders-"+random_number+".xls", data=data, overwrite=True)
               
def delete_blob(blob_client):
    blob_client_1 = blob_client.get_blob_client(container=container_name, blob="Exported_Orders-"+random_number+".xls")
    blob_client_1.delete_blob() 
    
def create_local_sheet_delete_unwanted_rows_cols(source_path, dest_path, sheet_name):
    data = pd.read_excel(source_path, sheet_name=sheet_name)
    #save it to the 'NewSheet' in destfile
    data.to_excel(dest_path, sheet_name='NewSheet')
    book = xl.load_workbook(dest_path)
    sheet = book['NewSheet']
    sheet.delete_rows(idx=1,amount=4)
    sheet.delete_cols(idx=1, amount=2)
    book.save(dest_path)
    
def watch_mongoDB_Discovery(MongoDB_URL, SKU_ID):
    logging.info("Inside dev instance of watch_mongoDB ")
    global updated_change, updated_json
    mongoClient = pymongo.MongoClient(MongoDB_URL)
    # logging.info(mongoClient)
    db = mongoClient["DigitalWallet"]
    logging.info(db.list_collection_names())
    db_collection = db["checkPointLicenses"]
    # logging.info(db_collection)
    query = {"skuId" : SKU_ID}
    try:
        for doc in db_collection.find(query):
            logging.info(doc)
    except:
        doc = None
        pass
    return doc

def watch_RabbitMQ_tester_publish(message_body):
    logging.info("Inside watch_RabbitMQ_tester_publish ")
    # make connection with RabbitMQ and get a channel
    credentials = pika.PlainCredentials(username, password)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE
    ssl_options = pika.SSLOptions(context)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            # ssl_options=ssl_options,
            port=5672,
            credentials=credentials,
        )
    )
    channel = connection.channel()
    logging.info(f"Connection to RabbitMQ Success")

    # data to be publish
    message = message_body

    # Publish the data into " task_queue"
    channel.basic_publish(
        exchange=aas_exchange,
        routing_key=publish_queue_tester,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()
    logging.info(f"Successfully published the message, Closing the connection.")

def watch_RabbitMQ_tester_consume(id):
    logging.info(f"Inside watch_RabbitMQ_tester_consume")
    credentials = pika.PlainCredentials(username, password)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE
    ssl_options = pika.SSLOptions(context)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            virtual_host=virtual_host,
            # ssl_options=ssl_options,
            port=5672,
            credentials=credentials,
        )
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        global status
        logging.info(f" [x] Received- {body}")
        consume_body = body.decode()
        consume_body = json.loads(consume_body)
        logging.info(f"Source ID is {consume_body['responses'][0]['source_id']}")
        if consume_body["responses"][0]["source_id"] == id:
            status = consume_body["responses"][0]["action_status"]
            channel.stop_consuming()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=consume_queue_tester, on_message_callback=callback)

    # listen to the queue
    channel.start_consuming()
    logging.info(f"Returning from watch_RabbitMQ_tester_consume")
    return status

def watch_mongoDB(MongoDB_URL, source_id_received):
    logging.info("Inside watch_mongoDB ")
    global updated_change, updated_json
    mongoClient = pymongo.MongoClient(MongoDB_URL)
    # logging.info(mongoClient)
    db = mongoClient["DigitalWallet"]
    logging.info(db.list_collection_names())
    db_collection = db["sdi.activations"]
    logging.info(db_collection)
    query = {"source_id" : source_id_received}
    for doc in db_collection.find(query):
       try:
           logging.info(doc)
       except:
           pass
    return doc

def validateJSON(data):
    json.loads(data)

def get_modified_payload(attribute, modified_data):
    logging.info(f"Inside get_modified_payload")
    with open("default_json.json", "r") as f:
        new = json.load(f)
    # updating the required fields with dummy data
    new["requests"][0][attribute] = modified_data
    source_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=31))
    new["requests"][0]["source_id"] = source_id
    # checking if the previous modified file present then delete it
    if os.path.exists("modified_json.json"):
        os.remove("modified_json.json")
    # creating the new modified/dummy payload
    with open("modified_json.json", "w") as ff:
        json.dump(new, ff)
    logging.info(f"Reurning from get_modified_payload")
    return source_id
