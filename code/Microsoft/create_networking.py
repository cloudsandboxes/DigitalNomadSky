def create_network(shared_data):
    import sys
    sys.path.append(r"C:/projects/digitalnomadsky/code/Microsoft")
    from azure.identity import InteractiveBrowserCredential
    import config
    from azure.mgmt.network import NetworkManagementClient
    from azure.core.exceptions import ResourceExistsError, HttpResponseError

    subscription_id = config.subscription_id
    resource_group = config.resource_group
    location = config.location
    vnet_base_name = 'vnet-vms'
    nic_base_name = 'nic-vm'
    
    tenant_id = config.destionationtenantid
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    vnet_index = 0
    x = 0

    while x != 1:
        try:
            address_prefix = f"10.0.{vnet_index}.0/29"
            vnet_name = f"{vnet_base_name}-{vnet_index}"
            subnet_name = "subnet-0"

            # Create VNet + Subnet
            vnet_params = {
                "location": location,
                "address_space": {"address_prefixes": [address_prefix]},
                "subnets": [
                    {"name": subnet_name, "address_prefix": address_prefix}
                ],
            }

            #vnet = network_client.virtual_networks.begin_create_or_update(
            #    resource_group, vnet_name, vnet_params
            #).result()
            vnet = network_client.virtual_networks.get(resource_group, vnet_name)
            vnet_index += 1

            #subnet = network_client.subnets.get(
            #    resource_group, vnet_name, subnet_name
            #)
            #break

        except HttpResponseError as e:
            if e.status_code == 404:
                 vnet = network_client.virtual_networks.begin_create_or_update(
                   resource_group, vnet_name, vnet_params
                    ).result()
                 subnet = network_client.subnets.get(
                   resource_group, vnet_name, subnet_name
                 )
                 x=1
            else:
                raise
    # Create NIC
    nic_params = {
        "location": location,
        "ip_configurations": [
            {
                "name": "ipconfig1",
                "subnet": {"id": subnet.id},
                "private_ip_allocation_method": "Dynamic",
            }
        ],
    }
    nic_name = f"{nic_base_name}-{vnet_index}"
    nic = network_client.network_interfaces.begin_create_or_update(
        resource_group, nic_name, nic_params
    ).result()
    return nic.id
