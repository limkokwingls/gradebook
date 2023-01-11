result = [{'key1': 'value1'}, {'key2': 'value2'}, {'key3': 'value1'}]

keys = [list(it.keys())[0] for it in result]
values = [list(it.values())[0] for it in result]

print(keys)
print()
print(values)