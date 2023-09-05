from sigma.collection import SigmaCollection
from sigma.pipelines.splunk import splunk_windows_pipeline
from sigma.pipelines.azure import azure_windows_pipeline
from sigma.backends.splunk import SplunkBackend
from sigma.backends.azure import AzureBackend
import pathlib
from pprint import pprint
import os

  
paths = []  
    
for path, subdirs, files in os.walk("rules"):
    for name in files:
        paths.append(os.path.join(path, name))
        
#print(paths)

rules = SigmaCollection.load_ruleset(paths)

#pprint(rules)

splunk_pipeline = splunk_windows_pipeline()
azure_pipeline = azure_windows_pipeline()
splunk_backend = SplunkBackend(splunk_pipeline)
azure_backend = AzureBackend(azure_pipeline)

splunk_rules = splunk_backend.convert(rules)
azure_rules = azure_backend.convert(rules)


for rule in rules:
    sigma_collection = SigmaCollection(rules=[rule])
    print(f"sigma rule: \n {sigma_collection}")
    with open("rules_convert/azure/"+rule.title.replace(" ","_")+".txt","w") as f:
        f.write("\n".join(azure_backend.convert(sigma_collection)))
    with open("rules_convert/splunk/"+rule.title.replace(" ","_")+".txt","w") as f:
        f.write("\n".join(splunk_backend.convert(sigma_collection)))

for rule in splunk_rules:
    print(f"spl rule:\n{rule}")

for rule in azure_rules:
    print(f"kql rule:\n{rule}")