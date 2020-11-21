# Export Confluence 

If you want to enable the export in confluence, in the settings/base.py set `EXPORT_CONFLUENCE` to True.

You need to set the env variables bellow
```
CONFLUENCE_URL = 'https://mycompany.atlassian.net'
CONFLUENCE_USER = myemail@mycompany.com
CONFLUENCE_TOKEN = [see the link to generate a token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html)
CONFLUENCE_SPACE = Name of the space you want your page to be in
CONFLUENCE_PARENT = Parent page id you want your page to be the child
```
