from sigma.collection import SigmaCollection
from sigma.pipelines.splunk import splunk_windows_pipeline
from sigma.pipelines.azure import azure_windows_pipeline
from sigma.backends.splunk import SplunkBackend
from sigma.backends.azure import AzureBackend
from sigma.processing.pipeline import ProcessingPipeline
from sigma.processing.resolver import ProcessingPipelineResolver
from ConvertedRule import ConvertedRule
import upload_to_sentinel
import upload_to_splunk
import pathlib
from pprint import pprint
import os
import json
import copy
import sys

def convert_to_query(sigma_folder):
    with open("azure_pipelines.yaml","r") as f:
        text = f.read()

    custom_azure_pipelines = ProcessingPipeline.from_yaml(text)

    resolver = ProcessingPipelineResolver()
    
    paths = []  
        
    for path, subdirs, files in os.walk(sigma_folder):
        for name in files:
            paths.append(os.path.join(path, name))
            
    #print(paths)

    rules = SigmaCollection.load_ruleset(paths)

    #pprint(rules)

    splunk_pipeline = splunk_windows_pipeline()
    azure_pipeline = azure_windows_pipeline()

    resolver.add_pipeline_class(azure_pipeline)
    resolver.add_pipeline_class(custom_azure_pipelines)
    real_azure_pipeline = resolver.resolve([azure_pipeline.name,custom_azure_pipelines.name])

    splunk_backend = SplunkBackend(splunk_pipeline)
    azure_backend = AzureBackend(real_azure_pipeline)
    azure_backend.eq_token = "=="

    splunk_rules = []
    azure_rules = []

    for rule in rules:
        sigma_collection_splunk = SigmaCollection(rules=[rule])
        sigma_collection_azure = copy.deepcopy(sigma_collection_splunk)
        
        splunk_rule = ConvertedRule(title = rule.title,
                                    id = rule.id,
                                    type="splunk",
                                    status=rule.status.name,
                                    rule=splunk_backend.convert(sigma_collection_splunk),
                                    severity=rule.level.name)
        azure_rule = ConvertedRule(title = rule.title,
                                   id=rule.id,
                                   type="azure",
                                   status=rule.status.name,
                                   rule=azure_backend.convert(sigma_collection_azure),
                                   severity=rule.level.name)
        splunk_rules.append(splunk_rule)
        azure_rules.append(azure_rule)
        # print(vars(splunk_rule))
        # print(vars(azure_rule))
        # with open("rules_convert/azure/"+rule.title.replace(" ","_")+".txt","w") as f:
        #     f.write(azure_rule.rule[0])
        # with open("rules_convert/splunk/"+rule.title.replace(" ","_")+".txt","w") as f:
        #     f.write(splunk_rule.rule[0])
    return splunk_rules, azure_rules

if __name__ == "__main__":
    sigma_rule_folder = "rules"
    if len(sys.argv) == 2:
        sigma_rule_folder = sys.argv[1]
    splunk_rules, azure_rules = convert_to_query(sigma_folder=sigma_rule_folder)
    upload_to_splunk.upload(splunk_rules)
    upload_to_sentinel.upload(azure_rules)
    