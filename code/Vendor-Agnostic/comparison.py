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
#VM_SIZE["azure"]["small"]

preferred_type = {
    "azure": {
        "import": ("vhd",),
        "export": ("vhd",)
    },
    "aws": {
        "import": ("vhd", "vmdk", "raw"),
        "export": ("vhd", "vmdk")
    },
    "huawei": {
        "import": ("vhd", "vmdk", "qcow2", "raw", "vhdx", "qcow", "vdi", "qed", "zvhd", "zvhd2"),
        "export": ("vhd", "vmdk", "qcow2", "raw")
    },
    "ibm": {
        "import": ("vhd", "qcow2", "raw"),
        "export": ("vhd", "qcow2")
    },
    "oracle": {
        "import": ("vmdk", "qcow2", "vhd"),
        "export": ("vmdk", "qcow2", "vhd")
    },
    "ovhcloud": {
        "import": ("qcow2", "raw", "vmdk"),
        "export": ("qcow2", "raw")
    },
    "stackit": {
        "import": ("qcow2", "raw", "vmdk", "vdi"),
        "export": ("qcow2", "raw")
    },
    "hetzner": {
        "import": ("raw", "qcow2"),
        "export": ("raw", "qcow2")
    },
    "gcp": {
        "import": ("vmdk", "vhd", "vhdx", "raw"),
        "export": ("vmdk", "raw")
    },
     "aliyun": {
        "import": ("vhd", "vmdk", "qcow2", "raw", "vhdx", "qcow", "vdi", "qed", "zvhd", "zvhd2"),
        "export": ("vhd", "vmdk", "qcow2", "raw")
    }, 
    "ecofed": {
        "import": ("raw"),
        "export": ("raw")
    }
}
