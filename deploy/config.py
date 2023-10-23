import os

LOG_LEVEL = 'INFO'

DEV = os.environ.get('DEV') == '1'

AWS_RES_NAME = 'Lab2'

AWS_KEY_PAIR_NAME = 'keypair_lab2'
AWS_SECURITY_GROUP_NAME = 'security_group_lab2'

M4_L_NB = 5
T2_L_NB = 4
IMAGE_ID = 'ami-053b0d53c279acc90'  # ubuntu 22.04
SSH_USERNAME = 'ubuntu'
