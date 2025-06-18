from awesome_list import generator


if __name__ == '__main__': 
    config, items, cats, tags = generator.parse_resource_items_yaml("./tests/resource_items.yaml")
print(type(items))
#for item in items: 
#    print(f"Item: {item["name"]} --> {item} ")
