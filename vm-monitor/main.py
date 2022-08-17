import requests
import json
import os
import base64
import time
from typing import Dict, Iterable
# pip install google-cloud-compute
from google.cloud import compute_v1


def send_msg(alert_msg):
    """
    把报警信息推送到企业微信的webhook
    """
    webhookurl = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxxxxxx"
    # webhookurl2 = os.getenv("webhookurl2")
    values = {
        "msgtype": "text",
        "text": {
            "content": alert_msg
        }
    }
    headers = {'Content-Type': 'application/json'}
    # 企业微信
    r = requests.post(webhookurl, json=values, headers=headers)
    # 企业微信
    # r2 = requests.post(webhookurl2, json=values, headers=headers)
    # 钉钉
    # r=requests.post(url,data=json.dumps(values),headers=headers)
    r.encoding = 'utf-8'
    return (r.text)


def list_all_instances() -> Dict[str, Iterable[compute_v1.Instance]]:
    """
    通过谷歌官方库，去获取实例信息。这里我们只需要内网ip
    Returns a dictionary of all instances present in a project, grouped by their zone.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
    Returns:
        A dictionary with zone names as keys (in form of "zones/{zone_name}") and
        iterable collections of Instance objects as values.
    """
    instance_client = compute_v1.InstancesClient()
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = "project_id"
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    request.max_results = 5000
    agg_list = instance_client.aggregated_list(request=request)
    all_instances = {}
    for zone, response in agg_list:
        if response.instances:
            for instance in response.instances:
                for ips in instance.network_interfaces:
                    all_instances[instance.id] = instance.name + "|" + ips.network_i_p
    # 返回一个字典，key为实例ID，value为实例名+内网IP
    return all_instances


def vm_alert(event, context):
    """
    封装具体的报警信息
    """
    inner_ip = list_all_instances() # 实例信息
    msg_decode = base64.b64decode(event['data']).decode('utf-8')
    msg = json.loads(msg_decode)
    status = msg['incident']['state']
    summary = msg['incident']['summary']
    started_at = time.ctime(msg['incident']['started_at'])
    ended_at = time.ctime(msg['incident']['ended_at'])
    project_id = msg['incident']['resource']['labels']['project_id']
    threshold_value = msg['incident']['threshold_value']
    observed_value = msg['incident']['observed_value']
    resource_display_name = msg['incident']['resource_display_name']
    policy_name = msg['incident']['policy_name']
    instance_id=msg['incident']['resource']['labels']['instance_id']

    alert_msg = "Google Alarm Details:\n" + "Current State:" + status + "\n" \
                 "started_at:" + started_at + "\n" \
                 "ended_at:" + ended_at + "\n" \
                 "Reason for State Change:" + summary + "\n" \
                 "报警策略：" + policy_name + "\n" \
                 "报警阈值：" + threshold_value + "\n" \
                 "当前值：" + observed_value + "\n" \
                 "实例名：" + resource_display_name + "\n" \
                 "实例内网IP：" + inner_ip[int(instance_id)]
    # 发送报警            
    res = send_msg(alert_msg)
