import os
import aiohttp
import asyncio
import json
import datetime

async def download_file(session, url, filepath, retry_count=3):
    if os.path.exists(filepath):
        print(f"{datetime.datetime.now()}: Skipping {filepath}, file already exists")
        return
    
    for attempt in range(1, retry_count + 1):
        try:
            async with session.get(url) as response:
                print(f'{datetime.datetime.now()}: Initiating download {filepath}')
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    print(f"{datetime.datetime.now()}: Downloaded {filepath}")

                else:
                    print(f'{datetime.datetime.now()}: Failed to download {filepath}')
        except Exception as e:
            print(f"{datetime.datetime.now()}: Attempt {attempt}: Error downloading {filepath}: {e}")
            if attempt == retry_count:
                print(f"{datetime.datetime.now()}: Failed to download {filepath} after {retry_count} attempts.")
                break

            await asyncio.sleep(2)


async def download_files_from_category(folder):
    json_files = [f for f in os.listdir(folder) if f.endswith('.json')]

    if not json_files:
        print(f'{datetime.datetime.now()}: No JSON file found in {folder}')
        return
    
    json_file = os.path.join(folder, json_files[0])
    with open(json_file) as f:
        data = json.load(f)
    
    tasks = []
    key = list(data.keys())[0]
    download_counter = 0
    async with aiohttp.ClientSession() as session:
        for item in data[key]['cases']:
            name = item['case_number'].replace('/', '-')
            url = item['file_download_url']

            filepath = f'{folder}/{name}.pdf'

            if os.path.exists(filepath):
                print(f"{datetime.datetime.now()}: Skipping {filepath}, file already exists")
                continue

            task = asyncio.create_task(download_file(session, url, filepath))
            tasks.append(task)

            download_counter += 1
            # if download_counter % 100 == 0:
            #     print(f'{datetime.datetime.now()}: ------------------- SLEEP: Downloaded 100 files, sleeping for 10 seconds ----------------------')
            #     await asyncio.sleep(10)
        
        await asyncio.gather(*tasks)


async def main():
    parent_folder = '/home/kafka/Class/CSI/data/files'
    folders = [os.path.join(parent_folder, d) for d in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, d)) and not d.startswith('.')]

    tasks = []
    for folder in folders:
        task = asyncio.create_task(download_files_from_category(folder))
        tasks.append(task)
        # print(f'\n ----------- SLEEP: 10 ------------ \n')
        # asyncio.sleep(10)
    
    await asyncio.gather(*tasks)

if __name__=="__main__":
    asyncio.run(main())