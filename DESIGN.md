# Awesome List Generator 

## TODO List 

- [X] Testing
  - [X] Testing: Scenarios 
- [ ] Categories 
  - [X] Categories: Sub Categories
  - [X] Categories: Hidden Categories
- [ ] Labels
  - [X] Labels: assigned to items 
  - [X] Labels: rendering in markdown 
- [X] Items
  - [ ] Items: types
  - [ ] Items: grouping 
  - [X] Items: labels 
  - [X] Items: Description override 
  - [X] Items: hidden items
- [X] Config
  - [X] Config: change file 
  - [X] Config: history 
  - [X] Config: category sorts
- [ ] Resource Types
  - [X] Resource Types: generic web-page support
  - [X] Resource Types: generic web-page: check if URL is still valid if not hide item
  - [X] Resource Types: generic web-page: extened metadata 
  - [X] Resource Types: Github
  - [X] Resource Types: Github: check if project is valid
  - [X] Resource Types: Github: extended project metadata
- [ ] Change Log
  - [X] Change Log: latest-changes file as markdown diff
  - [X] Change Log: latest-changes in the history folder 
- [ ] GitHub Template - Awesome List repository template - https://github.com/derekvincent/awesome-list-template
  - [X] GitHub Template: Created 
  - [X] GitHub Template: Issue templates 
  - [X] GitHub Template: PR templates 
  - [X] GitHub Template: Template filed (footer, header, base conifg)
  - [X] GitHub Template: Workflow Action --> Setup 
  - [X] GitHub Template: Workflow Action --> Scheduled List Update 
  - [X] GitHub Template: Workflow Action --> Set the release and publish webpage on a PR 
  - [X] GitHub Template: Documentation 
- [X] Awesome List Generator Action - https://github.com/derekvincent/action-awesome-list-updater
  - [X] Create a GitHub action to be used in the in updater action 
- [ ] Documentation
  - [X] Documentation: Readme 
  - [X] Documentation: Getting started 
  - [X] Documentation: Configuration/Usage 
  - [X] Documentation: Development 
  - [ ] Documentation: Support 
- [X] Build and Publish 
  - [X] Build and Publish: Workout build process 
  - [X] Build and Publish: Publish a package for the generator to PyPi 
  - [X] Build and Publish: Setup Generator repo for support etc.

## Config  
### Config Options 

|Property|Description|Default|
|--------|-----------|-------|
|output_file| Outfile name |README.md|
|latest_changes_file| Change file name  |latest-changes.md|
|awesome_history_folder| Folder to store the history |history|
|default_category| Name of the default category for item not correctly set | other|
|category_sort| Sorts the Categories by the following: set, asc, desc|set|
|list_title| The displayed title of the list |Awesome List!|
|feedback_api_url| Optional URL endpoint for creating GitHub issues from the web UI | blank |

## Categories 
### Category Properties 

|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|category| The ID of category, it is included in the item| N | |
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
|description| description| Y | blank |



## Items 
#### Item Properties 
|Property|Description|Optional| Default|
|--------|-----------|--------|--------|
|name| Name of the project and is required to be unique in the list. | N | |
| link_id | The url to the item | N | blank|
| type | The type of resources referenced from type property | N | webpage |
| category | Category of the resource item defined in the category section of the `resources.yaml` file. | N | other |
| labels | List of labels that relate to this resources item as defined in the `resources.yaml` file. | N | blank |
| description | A short description of the resource item, if empty a description will attempted to be set by the resource item discovery. | N | blank |
| published_at | The published date will be auto populated based on the resources item, if it can not be determined it will be left blank. | N | blank | 
| update_at | The published date will be auto populated based on the resources item, if it can not be determined it will be left blank. | N | blank |
| thumbnail_url | URL to a preview image (e.g., YouTube thumbnail, podcast cover art). | Y | blank |
| video_embed_url | Direct URL for embedding a video. | Y | blank |
| audio_embed_url | Direct URL for embedding audio. | Y | blank |
| media_type | The type of media (e.g., `video.other`, `audio/mpeg`). | Y | blank |
| duration | Duration of video/audio (e.g., `PT1H2M3S` for 1 hour, 2 minutes, 3 seconds). | Y | blank |
| latest_episode_title | For podcasts, the title of the most recent episode. | Y | blank |
| latest_episode_date | For podcasts, the publication date of the most recent episode. | Y | blank |

## Resource Type

These are pre-set. They define the Resource processor that will be used. Need to really determine what of this is useful. 

#### Resource Type Properties
|Property|Description|
|--------|-----------|
|webpage| Generic Webpage or article|
|article| News article or post |
|blog| Blog post |
|newsletter| News Letters|
|github| Github project |
