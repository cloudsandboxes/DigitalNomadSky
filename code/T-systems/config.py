# configuation parameters for T-systems cloud

# Your application credential is to login to your cloud environment 
OS_APPLICATION_CREDENTIAL_ID = '6e064903743147188cf917074e71d06c'
sourcelocation = 'eu-nl' # to complete the url
destinationlocation = 'eu-nl' # to complete the url
sourcecloudurl = f"https://iam.{sourcelocation}.otc.t-systems.com:443/v3"  # location of the current cloud environment


# Destination parameters:
nics = [{"net-id": "ee54f79e-d33a-4866-8df0-4a4576d70243"}]  #network id
destinationcloudurl = sourcecloudurl = f"https://iam.{destinationlocation}.otc.t-systems.com:443/v3"  
