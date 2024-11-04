# crawl new page from tfc
cd tfc_crawler
scrapy crawl tfc_spider -o ../.src/spd_tfc_data.json
cd ..

# merge new page with existing
python3 merge_tfc.py .src/tfc_data.json .src/spd_tfc_data.json .src/tfc_data.json
rm .src/spd_tfc_data.json

# renew rvs_tfc_data.json
python3 purify_tfc.py 

echo "Document merge completed!"