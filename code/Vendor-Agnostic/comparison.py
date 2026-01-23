VM_SIZES = {
    "azure": {
        "small": "Standard_B2ms",
        "medium": "Standard_D4s_v5",
        "large": "Standard_E8s_v5"
    },
    "aws": {
        "small": "t3.medium",
        "medium": "m5.xlarge",
        "large": "r5.2xlarge"
    },
    "gcp": {
        "small": "e2-standard-2",
        "medium": "n2-standard-4",
        "large": "n2-standard-8"
    },
    "huawei": {
        "small": "s6.large.2",
        "medium": "c6.xlarge.2",
        "large": "m6.2xlarge.8"
    },
    "oracle": {
        "small": "VM.Standard.E4.Flex",  # 2 OCPU, 16 GB
        "medium": "VM.Standard.E4.Flex",  # 4 OCPU, 32 GB
        "large": "VM.Standard.E5.Flex"   # 8 OCPU, 64 GB
    },
    "ibm": {
        "small": "bx2-2x8",
        "medium": "bx2-4x16",
        "large": "mx2-8x64"
    },
    "alibaba": {
        "small": "ecs.g6.large",
        "medium": "ecs.g6.xlarge",
        "large": "ecs.r6.2xlarge"
    }
}
