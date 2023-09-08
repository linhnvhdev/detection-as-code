from sigma.collection import SigmaCollection
from sigma.pipelines.splunk import splunk_windows_pipeline
from sigma.pipelines.azure import azure_windows_pipeline
from sigma.backends.splunk import SplunkBackend
from sigma.backends.azure import AzureBackend
from sigma.processing.pipeline import ProcessingPipeline
from sigma.processing.resolver import ProcessingPipelineResolver
import pathlib
from pprint import pprint
import os

with open("azure_pipelines.yaml","r") as f:
    text = f.read()

custom_azure_pipelines = ProcessingPipeline.from_yaml(text)

resolver = ProcessingPipelineResolver()
  
paths = []  
    
for path, subdirs, files in os.walk("rules"):
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

splunk_rules = splunk_backend.convert(rules)
azure_rules = azure_backend.convert(rules)


for rule in rules:
    sigma_collection = SigmaCollection(rules=[rule])
    with open("rules_convert/azure/"+rule.title.replace(" ","_")+".txt","w") as f:
        f.write("\n".join(azure_backend.convert(sigma_collection)))
    with open("rules_convert/splunk/"+rule.title.replace(" ","_")+".txt","w") as f:
        f.write("\n".join(splunk_backend.convert(sigma_collection)))
        
print("Nice!")