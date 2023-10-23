LOG_LEVEL = 'INFO'

LB_NAME = 'Lab2'
CLUSTER_1_PATH = '/cluster1'
CLUSTER_1_TARGET_NAME = f"{LB_NAME}-1"
CLUSTER_2_PATH = '/cluster2'
CLUSTER_2_TARGET_NAME = f"{LB_NAME}-2"

GRAPH_INFO = {
    'ActiveConnectionCount': {
        'TITLE': 'Active Connection Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of active TCP Connection per times'
    },
    'ConsumedLCUs': {
        'TITLE': 'Consumed LCUs',
        'XLABEL': 'Timestamps',
        'YLABEL': 'Price (USD)'
    },
    'HTTP_Redirect_Count': {
        'TITLE': 'HTTP Redirect Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of redirect actions that were successful'
    },
    'RuleEvaluations': {
        'TITLE': 'Rule Evaluations',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of rules processed'
    },
    'RequestCount': {
        'TITLE': 'Request Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of requests processed'
    },
    'ProcessedBytes': {
        'TITLE': 'Processed Bytes',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of bytes processed by loadbalancer (Bytes)'
    },
    'HTTPCode_Target_2XX_Count': {
        'TITLE': 'HTTP Code Target 2XX Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# HTTP response by targets'
    },
    'HealthyHostCount': {
        'TITLE': 'Healthy Host Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of targets that are considered healthy'
    },
    'TargetConnectionErrorCount': {
        'TITLE': 'Target Connection Error Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of connections that were not successfully established between the loadBalancer and target'  # noqa
    },
    'TargetResponseTime': {
        'TITLE': 'Target Response Time',
        'XLABEL': 'Timestamps',
        'YLABEL': 'Time elapsed (Second) after the request leaves the loadBalancer until a response from the target is received'  # noqa
    },
    'UnHealthyHostCount': {
        'TITLE': 'Unhealthy Host Count',
        'XLABEL': 'Timestamps',
        'YLABEL': '# of targets that are considered unhealthy'
    }
}
