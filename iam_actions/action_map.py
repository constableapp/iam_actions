# SPDX-License-Identifier: MIT
# Copyright 2020-2022 Big Bad Wolf Security, LLC

"""Define and create action structures.

Calling `create_action_map` with a dict from the services module is the
main entry point for this module.
"""

import json
import urllib.request
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, field
from enum import Enum

__all__ = ["create_action_map"]

# Formerly: https://docs.aws.amazon.com/IAM/latest/UserGuide
BASE_URL = "https://docs.aws.amazon.com/service-authorization/latest/reference"
TABLE_URL_TEMPLATE = BASE_URL + "/list_{}.html"
TOC_URL = BASE_URL + "/toc-contents.json"

URL_MAP = {
    "a2i-runtime.sagemaker": ["amazonsagemaker"],
    "a4b": ["alexaforbusiness"],
    "access-analyzer": ["awsiamaccessanalyzer"],
    "account": ["awsaccountmanagement", "awsaccounts"],
    "acm-pca": ["awscertificatemanagerprivatecertificateauthority"],
    "acm": ["awscertificatemanager"],
    "activate": ["awsactivate"],
    "airflow": ["amazonmanagedworkflowsforapacheairflow"],
    "amplify": ["awsamplify"],
    "amplifybackend": ["awsamplifyadmin"],
    "amplifyuibuilder": ["awsamplifyuibuilder"],
    "apigateway": [
        "manageamazonapigateway",
        "amazonapigatewaymanagementv2",
        "amazonapigatewaymanagement",
    ],
    "app-integrations": ["amazonappintegrations"],
    "appconfig": ["awsappconfig"],
    "appflow": ["amazonappflow"],
    "application-autoscaling": [
        "applicationautoscaling",
        "awsapplicationautoscaling",
    ],
    "application-cost-profiler": ["awsapplicationcostprofilerservice"],
    "applicationinsights": [
        "amazoncloudwatchapplicationinsights",
        "cloudwatchapplicationinsights",
    ],
    "appmesh-preview": ["awsappmeshpreview"],
    "appmesh": ["awsappmesh"],
    "apprunner": ["awsapprunner"],
    "appstream": ["amazonappstream2.0"],
    "appsync": ["awsappsync"],
    "aps": ["amazonmanagedserviceforprometheus"],
    "arsenal": ["applicationdiscoveryarsenal"],
    "artifact": ["awsartifact"],
    "athena": ["amazonathena"],
    "auditmanager": ["awsauditmanager"],
    "autoscaling-plans": ["awsautoscaling"],
    "autoscaling": ["amazonec2autoscaling"],
    "aws-marketplace-management": ["awsmarketplacemanagementportal"],
    "aws-marketplace": [
        "awsmarketplace",
        "awsmarketplacecatalog",
        "awsmarketplaceentitlementservice",
        "awsmarketplaceimagebuildingservice",
        "awsmarketplacemeteringservice",
        "awsmarketplaceprivatemarketplace",
        "awsmarketplaceprocurementsystemsintegration",
        "awsprivatemarketplace",
    ],
    "aws-portal": ["awsbilling"],
    "awsconnector": ["awsconnectorservice"],
    "backup-gateway": ["awsbackupgateway"],
    "backup-storage": ["awsbackupstorage"],
    "backup": ["awsbackup"],
    "batch": ["awsbatch"],
    "billingconductor": ["awsbillingconductor"],
    "braket": ["amazonbraket"],
    "budgets": ["awsbudgetservice"],
    "bugbust": ["awsbugbust"],
    "cases": ["amazonconnectcases"],
    "cassandra": ["amazonkeyspacesforapachecassandra"],
    "ce": ["awscostexplorerservice"],
    "chatbot": ["awschatbot"],
    "chime": ["amazonchime"],
    "cloud9": ["awscloud9"],
    "clouddirectory": ["amazonclouddirectory"],
    "cloudformation": ["awscloudcontrolapi", "awscloudformation"],
    "cloudfront": ["amazoncloudfront"],
    "cloudhsm": ["awscloudhsm"],
    "cloudsearch": ["amazoncloudsearch"],
    "cloudshell": ["awscloudshell"],
    "cloudtrail": ["awscloudtrail"],
    "cloudwatch": ["amazoncloudwatch"],
    "codeartifact": ["awscodeartifact"],
    "codebuild": ["awscodebuild"],
    "codecommit": ["awscodecommit"],
    "codedeploy": ["awscodedeploy"],
    "codedeploy-commands-secure": ["awscodedeploysecurehostcommandsservice"],
    "codeguru-profiler": ["amazoncodeguruprofiler"],
    "codeguru-reviewer": ["amazoncodegurureviewer"],
    "codeguru": ["amazoncodeguru"],
    "codepipeline": ["awscodepipeline"],
    "codestar-connections": ["awscodestarconnections"],
    "codestar-notifications": ["awscodestarnotifications"],
    "codestar": ["awscodestar"],
    "cognito-identity": ["amazoncognitoidentity"],
    "cognito-idp": ["amazoncognitouserpools"],
    "cognito-sync": ["amazoncognitosync"],
    "comprehend": ["amazoncomprehend"],
    "comprehendmedical": ["amazoncomprehendmedical", "comprehendmedical"],
    "compute-optimizer": ["awscomputeoptimizer", "computeoptimizer"],
    "config": ["awsconfig"],
    "connect": ["amazonconnect"],
    "connect-campaigns": ["high-volumeoutboundcommunications"],
    "controltower": ["awscontroltower"],
    "cur": ["awscostandusagereport"],
    "databrew": ["awsgluedatabrew"],
    "dataexchange": ["awsdataexchange"],
    "datapipeline": ["awsdatapipeline"],
    "datasync": ["awsdatasync", "datasync"],
    "dax": ["amazondynamodbacceleratordax"],
    "dbqms": ["databasequerymetadataservice"],
    "deepcomposer": ["awsdeepcomposer"],
    "deeplens": ["awsdeeplens"],
    "deepracer": ["awsdeepracer"],
    "detective": ["amazondetective"],
    "devicefarm": ["awsdevicefarm"],
    "devops-guru": ["amazondevopsguru"],
    "directconnect": ["awsdirectconnect"],
    "discovery": ["awsapplicationdiscoveryservice", "applicationdiscovery"],
    "dlm": ["amazondatalifecyclemanager"],
    "dms": ["awsdatabasemigrationservice"],
    "drs": ["awselasticdisasterrecovery"],
    "ds": ["awsdirectoryservice"],
    "dynamodb": ["amazondynamodb"],
    "ebs": ["amazonelasticblockstore"],
    "ec2-instance-connect": ["amazonec2instanceconnect"],
    "ec2": ["amazonec2"],
    "ec2messages": ["amazonmessagedeliveryservice"],
    "ecr-public": ["amazonelasticcontainerregistrypublic"],
    "ecr": ["amazonelasticcontainerregistry"],
    "ecs": ["amazonelasticcontainerservice"],
    "eks": ["amazonelastickubernetesservice"],
    "elastic-inference": ["amazonelasticinference"],
    "elasticache": ["amazonelasticache"],
    "elasticbeanstalk": ["awselasticbeanstalk"],
    "elasticfilesystem": ["amazonelasticfilesystem"],
    "elasticloadbalancing": ["elasticloadbalancingv2", "elasticloadbalancing"],
    "elasticmapreduce": ["amazonelasticmapreduce"],
    "elastictranscoder": ["amazonelastictranscoder"],
    "elemental-activations": [
        "elementalactivations",
        "awselementalappliancesandsoftwareactivationservice",
    ],
    "elemental-appliances-software": ["awselementalappliancesandsoftware"],
    "elemental-support-cases": ["elementalsupportcases"],
    "elemental-support-content": ["elementalsupportcontent"],
    "emr-containers": ["amazonemroneksemrcontainers"],
    "emr-serverless": ["amazonemrserverless"],
    "es": [
        "amazonopensearchservice",
        "amazonelasticsearchservice",
        "amazonopensearchservicesuccessortoamazonelasticsearchservice",
    ],
    "events": ["amazoneventbridge"],
    "evidently": ["amazoncloudwatchevidently"],
    "execute-api": ["amazonapigateway"],
    "finspace": ["amazonfinspace"],
    "firehose": ["amazonkinesisfirehose"],
    "fis": ["awsfaultinjectionsimulator"],
    "fms": ["awsfirewallmanager"],
    "forecast": ["amazonforecast"],
    "frauddetector": ["amazonfrauddetector"],
    "freertos": ["amazonfreertos"],
    "fsx": ["amazonfsx"],
    "gamelift": ["amazongamelift"],
    "gamesparks": ["amazongamesparks"],
    "geo": ["amazonlocation"],
    "glacier": ["amazons3glacier"],
    "globalaccelerator": ["awsglobalaccelerator"],
    "glue": ["awsglue"],
    "grafana": ["amazonmanagedgrafana", "amazonmanagedserviceforgrafana"],
    "greengrass": ["awsiotgreengrassv2", "awsiotgreengrass"],
    "groundstation": ["awsgroundstation"],
    "groundtruthlabeling": ["amazongroundtruthlabeling"],
    "guardduty": ["amazonguardduty"],
    "health": ["awshealthapisandnotifications"],
    "healthlake": ["amazonhealthlake"],
    "honeycode": ["amazonhoneycode"],
    "iam": ["identityandaccessmanagement"],
    "identitystore": ["awsidentitystore"],
    "identity-sync": ["awsidentitysync", "awsidentitysynchronizationservice"],
    "imagebuilder": ["amazonec2imagebuilder"],
    "importexport": ["awsimportexportdiskservice"],
    "inspector": ["amazoninspector"],
    "inspector2": ["amazoninspector2"],
    "iot-device-tester": ["awsiotdevicetester"],
    "iot": ["awsiot"],
    "iot1click": ["awsiot1-click"],
    "iotanalytics": ["awsiotanalytics"],
    "iotdeviceadvisor": ["awsiotcoredeviceadvisor"],
    "iotevents": ["awsiotevents"],
    "iotfleethub": ["awsiotfleethubfordevicemanagement"],
    "iotfleetwise": ["awsiotfleetwise"],
    "iotjobsdata": ["awsiotjobsdataplane"],
    "iotroborunner": ["awsiotroborunner"],
    "iotsitewise": ["awsiotsitewise"],
    "iotthingsgraph": ["awsiotthingsgraph"],
    "iottwinmaker": ["awsiottwinmaker"],
    "iotwireless": ["awsiotcoreforlorawan"],
    "iq-permission": ["awsiqpermissions"],
    "iq": ["awsiq"],
    "ivs": ["amazoninteractivevideoservice"],
    "ivschat": ["amazoninteractivevideoservicechat"],
    "kafka": ["amazonmanagedstreamingforapachekafka"],
    "kafka-cluster": ["apachekafkaapisforamazonmskclusters"],
    "kafkaconnect": ["amazonmanagedstreamingforkafkaconnect"],
    "kendra": ["amazonkendra"],
    "kinesis": ["amazonkinesis"],
    "kinesisanalytics": ["amazonkinesisanalytics", "amazonkinesisanalyticsv2"],
    "kinesisvideo": ["amazonkinesisvideostreams"],
    "kms": ["awskeymanagementservice"],
    "lakeformation": ["awslakeformation"],
    "lambda": ["awslambda"],
    "launchwizard": ["launchwizard"],
    "lex": ["amazonlexv2", "amazonlex"],
    "license-manager": ["awslicensemanager"],
    "license-manager-user-subscriptions": [
        "awslicensemanagerusersubscriptions",
    ],
    "lightsail": ["amazonlightsail"],
    "logs": ["amazoncloudwatchlogs"],
    "lookoutequipment": ["amazonlookoutforequipment"],
    "lookoutmetrics": ["amazonlookoutformetrics"],
    "lookoutvision": ["amazonlookoutforvision"],
    "m2": ["awsmainframemodernizationservice"],
    "machinelearning": ["amazonmachinelearning"],
    "macie": ["amazonmacieclassic"],
    "macie2": ["amazonmacie"],
    "managedblockchain": ["amazonmanagedblockchain"],
    "marketplacecommerceanalytics": ["awsmarketplacecommerceanalyticsservice"],
    "mechanicalturk": ["amazonmechanicalturk"],
    "mediaconnect": ["awselementalmediaconnect"],
    "mediaconvert": ["awselementalmediaconvert"],
    "medialive": ["awselementalmedialive"],
    "mediaimport": ["amazonmediaimport"],
    "mediapackage-vod": ["awselementalmediapackagevod"],
    "mediapackage": ["awselementalmediapackage"],
    "mediastore": ["awselementalmediastore"],
    "mediatailor": ["awselementalmediatailor"],
    "memorydb": ["amazonmemorydb"],
    "mgh": ["awsmigrationhub"],
    "mgn": ["awsapplicationmigrationservice"],
    "migrationhub-orchestrator": ["awsmigrationhuborchestrator"],
    "migrationhub-strategy": ["awsmigrationhubstrategyrecommendations"],
    "mobileanalytics": ["amazonmobileanalytics"],
    "mobilehub": ["awsmobilehub"],
    "mobiletargeting": ["amazonpinpoint"],
    "monitron": ["amazonmonitron"],
    "mq": ["amazonmq"],
    "neptune-db": ["amazonneptune"],
    "network-firewall": ["awsnetworkfirewall"],
    "networkmanager": ["awsnetworkmanager", "networkmanager"],
    "nimble": ["amazonnimblestudio"],
    "opsworks-cm": ["awsopsworksconfigurationmanagement"],
    "opsworks": ["awsopsworks"],
    "organizations": ["awsorganizations"],
    "outposts": ["awsoutposts"],
    "panorama": ["awspanorama"],
    "personalize": ["amazonpersonalize"],
    "pi": ["awsperformanceinsights"],
    "polly": ["amazonpolly"],
    "pricing": ["awspricelist"],
    "private-networks": ["awsserviceprovidingmanagedprivatenetworks"],
    "profile": ["amazonconnectcustomerprofiles"],
    "proton": ["awsproton"],
    "purchase-orders": ["awspurchaseordersconsole"],
    "qldb": ["amazonqldb"],
    "quicksight": ["amazonquicksight"],
    "ram": ["awsresourceaccessmanager"],
    "rbin": ["awsrecyclebin"],
    "rds-data": ["amazonrdsdataapi"],
    "rds-db": ["amazonrdsiamauthentication"],
    "rds": ["amazonrds"],
    "redshift-data": ["amazonredshiftdataapi"],
    "redshift": ["amazonredshift"],
    "redshift-serverless": ["amazonredshiftserverless"],
    "refactor-spaces": ["awsmigrationhubrefactorspaces"],
    "rekognition": ["amazonrekognition"],
    "resiliencehub": ["awsresiliencehubservice"],
    "resource-explorer": ["awstageditor"],
    "resource-groups": ["awsresourcegroups"],
    "rhelkb": ["amazonrhelknowledgebaseportal"],
    "robomaker": ["awsrobomaker"],
    "rolesanywhere": ["awsidentityandaccessmanagementrolesanywhere"],
    "route53": ["amazonroute53"],
    "route53domains": ["amazonroute53domains"],
    "route53resolver": ["amazonroute53resolver"],
    "route53-recovery-cluster": ["amazonroute53recoverycluster"],
    "route53-recovery-control-config": ["amazonroute53recoverycontrols"],
    "route53-recovery-readiness": ["amazonroute53recoveryreadiness"],
    "rum": ["awscloudwatchrum"],
    "s3-outposts": ["amazons3onoutposts"],
    "s3": ["amazons3"],
    "s3-object-lambda": ["amazons3objectlambda"],
    "sagemaker": ["amazonsagemaker"],
    "sagemaker-groundtruth-synthetic": ["amazonsagemakergroundtruthsynthetic"],
    "savingsplans": ["awssavingsplans"],
    "schemas": ["amazoneventbridgeschemas"],
    "sdb": ["amazonsimpledb"],
    "secretsmanager": ["awssecretsmanager"],
    "securityhub": ["awssecurityhub"],
    "serverlessrepo": ["awsserverlessapplicationrepository"],
    "servicecatalog": ["awsservicecatalog"],
    "servicediscovery": ["awscloudmap"],
    "serviceextract": ["awsmicroserviceextractorfor.net"],
    "servicequotas": ["servicequotas"],
    "ses": [
        "amazonses",
        "amazonpinpointemailservice",
        "amazonsimpleemailservicev2",
    ],
    "shield": ["awsshield"],
    "signer": ["awssigner"],
    "sms-voice": [
        "amazonpinpointsmsandvoiceservice",
        "amazonpinpointsmsvoicev2",
    ],
    "sms": ["awsservermigrationservice"],
    "snowball": ["awssnowball"],
    "snow-device-management": ["awssnowdevicemanagement"],
    "sns": ["amazonsns"],
    "sqlworkbench": ["awssqlworkbench"],
    "sqs": ["amazonsqs"],
    "ssm": ["awssystemsmanager"],
    "ssmmessages": ["amazonsessionmanagermessagegatewayservice"],
    "ssm-incidents": ["awssystemsmanagerincidentmanager"],
    "ssm-contacts": ["awssystemsmanagerincidentmanagercontacts"],
    "ssm-guiconnect": ["awssystemsmanagerguiconnect"],
    "sso": ["awsiamidentitycentersuccessortoawssinglesign-on", "awssso"],
    "sso-directory": [
        "awsiamidentitycentersuccessortoawssinglesign-ondirectory",
        "awsssodirectory",
    ],
    "states": ["awsstepfunctions"],
    "storagegateway": ["awsstoragegateway", "amazonstoragegateway"],
    "sts": ["awssecuritytokenservice"],
    "sumerian": ["amazonsumerian"],
    "support": ["awssupport"],
    "sustainability": ["awssustainability"],
    "swf": ["amazonsimpleworkflowservice"],
    "synthetics": ["amazoncloudwatchsynthetics"],
    "tag": ["amazonresourcegrouptaggingapi"],
    "tax": ["awstaxsettings"],
    "textract": ["amazontextract"],
    "timestream": ["amazontimestream"],
    "tiros": ["awstiros"],
    "transcribe": ["amazontranscribe"],
    "transfer": ["awstransferfamily", "awstransferforsftp"],
    "translate": ["amazontranslate"],
    "trustedadvisor": ["awstrustedadvisor"],
    "vendor-insights": ["awsmarketplacevendorinsights"],
    "voiceid": ["amazonconnectvoiceid"],
    "waf-regional": ["awswafregional"],
    "waf": ["awswaf"],
    "wafv2": ["awswafv2"],
    "wam": ["amazonworkspacesapplicationmanager"],
    "wellarchitected": ["awswell-architectedtool"],
    "wisdom": ["amazonconnectwisdom"],
    "workdocs": ["amazonworkdocs"],
    "worklink": ["amazonworklink"],
    "workmail": ["amazonworkmail"],
    "workmailmessageflow": ["amazonworkmailmessageflow"],
    "workspaces": ["amazonworkspaces"],
    "workspaces-web": ["amazonworkspacesweb"],
    "xray": ["awsx-ray"],
}


class AccessLevel(str, Enum):
    """Enumerate the possible action "AccessLevel" item values."""
    READ = "Read"
    WRITE = "Write"
    PUT = "Put"
    DELETE = "Delete"
    GET = "Get"
    LIST = "List"
    PERMISSIONS_MANAGE = "Permissions management"
    TAGGING = "Tagging"
    REPLICATE = "Replicate"
    NONE = "None"
    UNDOCUMENTED = "Undocumented"

    def __repr__(self) -> str:
        """Represent `AccessLevel` items as their bare string values."""
        return self.value


@dataclass
class ActionMap:
    """Define the structure of an AWS action definition."""
    access_level: AccessLevel = AccessLevel.NONE
    action: str = ""
    condition_keys: list[str] = field(default_factory=list, repr=False)
    description: str = ""
    orphan: bool = False
    resources: list[str] = field(default_factory=list)


def find_actions_table(url: str) -> Tag | None:
    """Locate the actions table element in the web page.

    The table IDs seem to change, so search by div then look for the
    table headers that match the expected structure, e.g.:

        <div class="table-container">
            <div class="table-contents">
                <table id="w468aac34c13c27d782c11b9">
                    <tr>
                        <th>Actions</th>
                        <th>Description</th>
                        <th>Access Level</th>
                        <th>Resource Types (*required)</th>
                        <th>Condition Keys</th>
                        <th>Dependent Actions</th>
                    </tr>
    """
    # The headers seem to change capitalization randomly, so force lowercase.
    expected_headers = {
        "actions",
        "description",
        "access level",
        "resource types (*required)",
        "condition keys",
        "dependent actions",
    }

    with urllib.request.urlopen(url) as response:
        page = response.read()

    soup = BeautifulSoup(page, "html.parser")
    for div in soup.find_all("div", {"class": "table-contents"}):
        table = div.find_all("table")[0]  # There should be only one.
        headers = table.find_all("th")
        if expected_headers == {x.string.lower() for x in headers}:
            return table


def flatten_table(table: Tag) -> list[list[str]]:
    """Return a table element as a list of lists of strings.

    The AWS actions table sometimes can be a mess, so flatten it before
    doing any processing.  This involves tracking rowspans and
    concatenating table cells where appropriate.

    Assumptions:
    - The first cell of each row contains its maximum rowspan.
    - Cells for rows bound by the maximum rowspan can be concatenated.
    - The first row in a rowspan contains the required six cells.
    - If the first cell starts with SCENARIO, the AWS writer was drunk.
    """
    flat_table = []

    rows = (x for x in table if x.name == "tr")
    for row in rows:
        cells = [x for x in row if x.name == "td"]
        assert len(cells) == 6

        # Process a row by converting its cells to a list of strings.
        processed_row = [x.text.strip() for x in cells]
        rowspans = [int(x.get("rowspan", "1")) for x in cells]
        max_rowspan = rowspans[0]

        # Process any rows in a rowspan after the first.
        for _ in range(1, max_rowspan):
            row = next(rows)
            cells = [x for x in row if x.name == "td"]

            # There are some weird rows that should be to ignored, e.g.
            # ec2:RunInstance has a bunch of rows starting with "SCENARIO".
            ignore_row = "SCENARIO" in cells[0].text

            # Append each cell's text to the corresponding column.
            cells = iter(cells)
            for column in range(len(processed_row)):
                if rowspans[column] > 1:
                    rowspans[column] -= 1
                elif not ignore_row:
                    processed_row[column] += f" {next(cells).text.strip()}"
        assert all(x == 1 for x in rowspans)

        flat_table.append(processed_row)

    return flat_table


def process_actions_table(table: Tag) -> list[ActionMap]:
    """Return a list of actions, one per row of the given table."""
    return [
        ActionMap(
            action=row[0].replace("[permission only]", "").strip(),
            access_level=AccessLevel(row[2]),
            resources=sorted({x.replace("*", "") for x in row[3].split()}),
            condition_keys=sorted({x for x in row[4].split()}),
            description=" ".join(row[1].split()),
        )
        for row in flatten_table(table)
    ]


def generate_action_map(name: str, acts: list[str]) -> tuple[dict, list[str]]:
    """Return a tuple of service actions and any errors encountered.

    The given service name has its documentation URLs searched for
    action definitions.  They are then compared with the given known
    service action names to find undocumented actions.  The whole set of
    actions is then returned as a dict keyed on their names, alongside a
    list of any error messages.
    """
    errors = []

    url_names = URL_MAP.get(name, [])
    if not url_names:
        errors.append(f"Service missing URL map: {name}")

    actions = {}
    for url_name in url_names:
        table = find_actions_table(TABLE_URL_TEMPLATE.format(url_name))
        if not table:
            errors.append(f"Page missing actions table: {url_name}")
            continue
        for map in process_actions_table(table):
            # Keep the first one as defined in the URL map.
            if map.action not in actions:
                actions[map.action] = map

    # Check if any known actions are missing from the documentation.
    boto_defined_actions = set(acts)
    found_actions = set(actions.keys())
    for action in boto_defined_actions - found_actions:
        actions[action] = ActionMap(
            action=action,
            access_level=AccessLevel.UNDOCUMENTED,
            description="Not Documented by AWS",
        )
        errors.append(f"Undocumented action found: {name}:{action}")

    return actions, errors


def missing_services(url: str = TOC_URL) -> set[str]:
    """Return a set of undefined service names.

    AWS posts a TOC JSON object with all their services.  Its service
    names are compared to the URL map to detect if any are missing.
    """
    with urllib.request.urlopen(url) as response:
        toc = json.loads(response.read())
    toc_services = {
        service.get("href", "").removeprefix("list_").removesuffix(".html")
        for service in toc["contents"][0]["contents"][0]["contents"]
    }
    return toc_services - set(sum(URL_MAP.values(), []))


def create_action_map(services: dict) -> tuple[dict, list[str]]:
    """Return a map of AWS actions and a list of any errors."""
    errors = []

    # Verify all AWS services are defined here.
    for service in missing_services():
        errors.append(f"Unmapped service is being published: {service}")

    # Fetch and parse each service page.
    action_map = {}
    for name in sorted(services.keys()):
        print(f"Generating {name}")
        pmap, action_errors = generate_action_map(name, services[name].Actions)
        action_map[name] = pmap
        errors += action_errors

    return action_map, sorted(errors)