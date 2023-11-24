import os
end_user= 'Adidas Singapore Pte Ltd'
# MongoDB_URL = "mongodb://mongoRootAdmin:mongoRootAdmin@atl-az-we-tis-dw-dev-shard-00-00.seiqd.mongodb.net:27017,atl-az-we-tis-dw-dev-shard-00-01.seiqd.mongodb.net:27017,atl-az-we-tis-dw-dev-shard-00-02.seiqd.mongodb.net:27017/?ssl=true&replicaSet=atlas-31rrlc-shard-0&authSource=admin&retryWrites=true&w=majority"
MongoDB_URL = "mongodb://admin:Admin123@172.26.224.58:27017/"
storage_account_name = "sdidwcheckpointuat"
container_name = "checkpoint-workbooks"
AccountKey = "54X3EJGbzAt9r7Xp16SSViAlCBsNXXm2vgDOZ7Cg8DIiAjGwlXSDJvRY4o9Mr8Oeo52dGlx5Ewv9+AStD9ZcDA=="
connect_str = "DefaultEndpointsProtocol=https;AccountName="+storage_account_name+";AccountKey="+AccountKey+";EndpointSuffix=core.windows.net"
path = os.path.join(os.getcwd(), 'TESTING.xls')
product_list_path = os.path.join(os.getcwd(), 'Product_List.xlsx')
dest_overview = os.path.join(os.getcwd(), 'TESTING_overview.xlsx')
dest_product = os.path.join(os.getcwd(), 'TESTING_product.xlsx')
dest_standalone = os.path.join(os.getcwd(), 'TESTING_standalone.xlsx')
dest_support = os.path.join(os.getcwd(), 'TESTING_support.xlsx')
username = "SDI_checkpoint-uat-tester"
password = "Yd33kP136oxp"
# host = "emr.dev.splat.nttltd.global.ntt"
host = "172.26.224.58"
virtual_host = "MSP"
aas_exchange = "AAS"
publish_queue_tester = "AAS.REQUEST.OUTBOUND.CHECKPOINT_LICENSE_DISCOVERY"
publish_queue_tester_nifi = "AAS2.REQUEST.OUTBOUND.CHECKPOINT_LICENSE_DISCOVERY"
consume_queue_tester_nifi = "_test_aas_response_inbound_checkpoint_licence_discovery"
consume_queue_tester = "_test2_aas_response_inbound_checkpoint_licence_discovery"
routing_key_consume_service_ = "AAS.REQUEST.OUTBOUND.CHECKPOINT_LICENSE_DISCOVERY"
