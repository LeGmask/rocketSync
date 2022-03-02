import os
import json
from tqdm import tqdm

from src.gdrive import Drive
from src.utils import formatName, getTag, removeTag



with open(os.path.join(os.path.dirname(__file__), './config.json'), encoding='utf-8') as file:
	config = json.load(file)

drive = Drive(config)

for file_name, file_id in tqdm(drive.get_rocketTemp().items()):
    name, ext = os.path.splitext(file_name)
    
    tag = getTag(name) # if file is a class file (tag <=> UE name)

    if tag: # if school file
        name = removeTag(name, tag)
        path = config['DISK']['path'] 
        
        drive.downloadFile(
            file_name=f"{config['DISK']['prefix']}_{formatName(name)}{ext}",
            file_id=file_id,
            file_path=f'{config["DISK"]["path"]}/{tag}'
        )

        cours_children = drive.listChildrenFolder("1FtNPgSY0S7kTxDL2yOlN09-VWk8rhrd4")
        if tag not in drive.listChildrenFolder("1FtNPgSY0S7kTxDL2yOlN09-VWk8rhrd4").keys():
            cours_children[tag] = drive.createFolder(tag, parents=[config["GDRIVE"]["RocketCoursId"]]);
        
        drive.moveFile(file_id, cours_children[tag])

    else:
        drive.moveFile(file_id, config["GDRIVE"]["RocketSyncId"])
        
