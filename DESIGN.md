# Awesome List Generator 

## TODO List 

- [X] Categories 
- [X] Categories: Sub Categories
- [ ] Categories: Hidden Categories
- [X] Labels 
- [X] Items
- [ ] Items: types
- [ ] Items: grouping 
- [X] Items: labels 
- [ ] Items: Description override 
- [ ] Items: hidden items
- [X] Config
- [X] Config: change file 
- [X] Config: history 
- [ ] Config: category sorts
- [ ] Resource Types 
- [ ] Change Log
- [X] Change Log: latest-changes file as markdown diff
- [X] Change Log: latest-changes in the history folder 

## Config  
### Config Options 

|Property|Description|Default|
|--------|-----------|-------|
|output_file| Outfile name |README.md|
|latest_changes_file| Change file name  |latest-changes.md|
|awesome_history_folder| Folder to store the history |history|
|default_category| Name of the default category for item not correctly set | other|
|category_sort| Sorts the Categories by the following: set, asc, desc|set|
|list_title| The displayed title of the list |Awsome List!|

## Categories 
### Category Properties 

|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|category| The ID of category, it is inlcuded in the item| N | |
|name| Category name used for display| N | | 
|description| A description of the category | Y | blank |
|parent| Sets the parent category for a subcategory item | Y | blank |
|hidden| If True the category is not used| Y | False |

## Labels 

The label will be used for the classification of 
### Labels Properties

|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|label| The ID of the label| N | |
|icon| URL to an icon | Y | blank |
|description| descripton| Y | blank |



## Items 
#### Item Properties 
|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|name| Name of the project and is required to be unique in the list. | N | |
| link_id | The url to the item | N | blank|
| type | The type of resources referenced from type property | N | webpage |
| category | Category of the resource item defined in the category section of the `resources.yaml` file. | N | other |
| labels | List of lables that relate to this resources item as definedin in the `resources.yaml` file. | N | blank |
| description | A short description of the resource item, if empty a description will attempted to be set by the resource item discovery. | N | blank |
| published_at | The published date will be auto populated based on the resources item, if it can not be determined it will be left blank. | N | blank | 
| update_at | The published date will be auto populated based on the resources item, if it can not be determined it will be left blank. | N | blank |

## Resource Type

These are pre-set. The define the Resource processor that will be used. Need to really determine what of this is usefully. 

#### Resource Type Properties
|Property|Description|
|--------|-----------|
|webpage| Generic Webpage or article|
|article| News article or post |
|blog| Blog post |
|newsletter| News Letters|
|github| Github project |

