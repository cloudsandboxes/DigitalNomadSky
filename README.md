# Nomadsky Digital Sovereignty

## Stay Digitally Sovereign. Move Your Server Workloads to Anywhere.

Take full control over where your applications run in any cloud or infrastructure. No vendor lock-in. No friction. Complete oversight of location, costs, and compliance — from Azure to ZeroCloud and everything in between.
Check our demo, [here](https://htmlpreview.github.io/?https://github.com/cloudsandboxes/nomadsky/blob/main/code/nomadsky-engine/UI/demo/interface.html)

### Key Benefits


* **Eliminate Vendor Lock-In:** Move workloads freely as costs, performance, or policies change.
* **Full Data Sovereignty:** Decide exactly where your data resides — by country, region, or provider.
* **Flexible Cloud Ecosystem:** Combine public clouds, European providers, and your own data centers.
* **Seamless Migration:** One platform that makes cloud switching predictable, manageable, and low-risk.
* **Environment friendly:** Chose the cloud with the lowest CO2 emission rates.

# Process Design


                   .--------------------------.
                  /                          /|
                 '         Nomadsky         / |
                +--------------------------+  |
                |           engine         |  +
                |                          | /
                '--------------------------'  
                  ^                    |
                  |                    |
                  |1) Download image   | 1) upload image
                  |                    |
                  |                    V
            .---------.             .---------.
          /          /|            /          /|
         '    VM 1  / |           '    VM 2  / |
        +----------+  |          +----------+  |
        |          |  +          |          |  +
        |          | /           |          | /
        '----------'             '----------'


### Step 1: Download image.
The code for this step is in folder named "Download images", and it depends on the vendor you are migrating from. 

### Step 2: upload image.
The code for this step is in folder named "upload images", and it depends on the vendor you are migrating to.

### Nomadsky engine
The code for the nomadsky engine is based on different features, which could be run like independent modules. 
1) Ground level code execution
2) transformation between VHD  or VMDK OS-format.




 ## Scope
 In this project you can migrate VMs with the following characteristics: 
 * Only single disk support,
 * Max size of the VM depends on the size of the Nomadsky Engine
 * No licences are transfered (for example Windows, SQL or Redhat licenses)
 * Check hardware limits for example GPU's work different between providers.

## Get started:
1) Clone the repo, 



