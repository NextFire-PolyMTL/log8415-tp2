import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import orjson

from bench.config import GRAPH_INFO
from bench.utils import cw_cli, specifier_from_arn, target_group_name_from_arn

if TYPE_CHECKING:
    from mypy_boto3_cloudwatch.type_defs import (
        DimensionTypeDef,
        MetricDataResultTypeDef,
    )

logger = logging.getLogger(__name__)


def analyze(lb_arn: str,
            start_time: datetime,
            end_time: datetime,
            tg_arn: str | None = None):
    data, path = _save_metrics_data(
        lb_arn, start_time, end_time, tg_arn=tg_arn)
    _generate_graph(path.parent, data, tg_arn)


def _generate_graph(basedir: Path,
                    data: list['MetricDataResultTypeDef'],
                    tg_arn: str | None = None):
    for item in data:
        label = item.get('Label')
        timestamps = item.get('Timestamps')
        values = item.get('Values')

        if label is None or timestamps is None or values is None:
            raise ValueError(
                f"Missing label, timestamps or values for {item=}")

        active_connection_timestamps = list(
            map(lambda t: t.strftime(r'%Y-%m-%d %H:%M'), reversed(timestamps)))
        active_connection_values = list(reversed(values))

        if len(active_connection_timestamps) > 0:
            x_axis = np.arange(len(timestamps))
            _create_graph(basedir,
                          active_connection_timestamps,
                          active_connection_values,
                          x_axis,
                          label,
                          tg_arn)


def _addLabels(x: list[str], y: list[float]):
    """Add value labels in the graph"""
    for i in range(len(x)):
        plt.text(i, y[i], str(y[i]), ha='center')


def _create_graph(basedir: Path,
                  abscissa: list[str],
                  ordinate: list[float],
                  x_axis: np.ndarray,
                  itemLabel: str,
                  tg_arn: str | None = None):
    fig = plt.figure(figsize=(10, 10))
    # fig.suptitle(GRAPH_INFO[itemLabel]['TITLE'])
    ax = fig.add_subplot(111)
    ax.bar(abscissa, ordinate)
    ax.set_xticklabels(abscissa, rotation=45)
    _addLabels(abscissa, ordinate)
    plt.xlabel(GRAPH_INFO[itemLabel]['XLABEL'])
    plt.ylabel(GRAPH_INFO[itemLabel]['YLABEL'])
    plt.plot(x_axis, ordinate, color="red")

    suffix = target_group_name_from_arn(tg_arn)

    plt.savefig(basedir / f"{suffix}_{itemLabel}.png")
    # plt.show()


def _save_metrics_data(lb_arn: str,
                       start_time: datetime,
                       end_time: datetime,
                       tg_arn: str | None = None):
    data = _get_metric_data(lb_arn, start_time, end_time, tg_arn)
    base_dir = Path(f"./results/{start_time.strftime(r'%Y-%m-%dT%H_%M')}")
    if not base_dir.exists():
        os.mkdir(base_dir)
    filename = f"{target_group_name_from_arn(tg_arn)}.json"
    path = base_dir / filename
    with open(path, 'wb') as f:
        dump = orjson.dumps(data)
        f.write(dump)
    return data, path


def _get_metric_data(lb_arn: str,
                     start_time: datetime,
                     end_time: datetime,
                     tg_arn: str | None = None):
    lb_specifier = specifier_from_arn(lb_arn)
    dimensions: list['DimensionTypeDef'] = [
        {
            'Name': 'LoadBalancer',
            'Value': lb_specifier
        }
    ]
    if tg_arn is not None:
        tg_specifier = specifier_from_arn(tg_arn)
        dimensions.append({
            'Name': 'TargetGroup',
            'Value': tg_specifier
        })
    data = cw_cli.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'myrequest_RequestCount',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'RequestCount',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_ActiveConnectionCount',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'ActiveConnectionCount',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_ConsumedLCUs',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'ConsumedLCUs',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_HTTP_Redirect_Count',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'HTTP_Redirect_Count',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_RuleEvaluations',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'RuleEvaluations',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_ProcessedBytes',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'ProcessedBytes',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Bytes'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_HTTPCode_Target_2XX_Count',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'HTTPCode_Target_2XX_Count',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_HealthyHostCount',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'HealthyHostCount',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Average',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_TargetConnectionErrorCount',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'TargetConnectionErrorCount',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Sum',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_TargetResponseTime',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'TargetResponseTime',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Average',
                    'Unit': 'Seconds'
                },
                'ReturnData': True,
            },
            {
                'Id': 'myrequest_UnHealthyHostCount',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName': 'UnHealthyHostCount',
                        'Dimensions': dimensions
                    },
                    'Period': 60,
                    'Stat': 'Average',
                    'Unit': 'Count'
                },
                'ReturnData': True,
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
    )
    return data['MetricDataResults']
