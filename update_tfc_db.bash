set -e  # Exit on any command failure
set -o pipefail  # Exit if any command in a pipeline fails

temp_json="/Users/hsiangan/Desktop/RAGuard/.src/spd_tfc_data.json"
org_json="/Users/hsiangan/Desktop/RAGuard/.src/tfc_data.json"

# fetch new data
echo "Fetching new data..."
cd tfc_crawler
scrapy crawl tfc_spider -o $temp_json
cd ..

# upsert new data into database
echo "Upserting new data to Pinecone..."
python tfc_upsert.py --input_file $temp_json


# merge data to exist data
echo "Merging data..."
python3 tfc_merge.py $org_json $temp_json $org_json
rm $temp_json
echo "Temporary file removed."