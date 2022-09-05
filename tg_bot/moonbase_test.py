from substrateinterface import SubstrateInterface



url = "ws://127.0.0.1:9954"
substrate = SubstrateInterface(
    url=url
)   
result = substrate.query(
    module='ParachainStaking',
    storage_function='CandidatePool'
)

print(result)



