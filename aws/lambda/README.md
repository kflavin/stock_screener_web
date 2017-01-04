# How to build
This code is intended to be used as an AWS Lambda function.  Currently, just a copy of the populators/ folder.

```bash
cd sectors
zip -r ../sectors.zip .
aws lambda create-function --function-name populate_sectors --runtime python2.7 --role <role ARN> --handler sectors.handle_sectors --zip-file fileb://../sectors.zip
```

Subsequent updates

```bash
aws lambda update-function-code --function-name populate_sectors --zip-file fileb://../sectors.zip
```
