


## Categories 
### Category Properties 

|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|category| The ID of category, it is inlcuded in the item| N | |
|name| Category name used for display| N | | 
|description| A description of the category | Y | blank |
|hidden| If True the category is not used| Y | False |

## Tags 
### Tag Properties

|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|tag| The ID of the tag| N | |
|name| Name of the tag| Y | tag |
|description| descripton| Y | blank |
|hidden| hidden | Y | False |


## Items 
#### Item Properties 
|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|name| Name of the project and is required to be unique in the list. | N | |
| link_id | The url to the item | N | blank|
| type | The type of resources referenced from type property | N | webpage |
| category | Category of the resource item defined in the category section of the `resources.yaml` file. | N | other |
| tags | List of tags that relate to this resources item as definedin in the `resources.yaml` file. | N | blank |
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

