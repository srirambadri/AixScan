import cv2
import os
import time
import csv

CSV_FILE=r"C:\Users\Tharun Balaji\Downloads\objects.csv"
SAVE_FOLDER=r"C:\Users\Tharun Balaji\Downloads\newimages"

VALID_OBJECTS={"cable","smartphone","feature phone"}

os.makedirs(SAVE_FOLDER,exist_ok=True)

if not os.path.exists(CSV_FILE):
    print(f"CSV file not found: {CSV_FILE}")
    exit()

with open(CSV_FILE,"r",newline="",encoding="utf-8-sig") as file:
    reader=csv.DictReader(file)

    if reader.fieldnames is None:
        print("CSV file is empty.")
        exit()

    reader.fieldnames=[field.strip().lower() for field in reader.fieldnames]

    if "object name" not in reader.fieldnames or "count" not in reader.fieldnames:
        print("CSV must contain these columns:")
        print("object name,count")
        exit()

    rows=[]

    for row in reader:
        object_name=row["object name"].strip().lower()

        try:
            count=int(row["count"])
        except:
            print(f"Invalid count for {object_name}")
            exit()

        if object_name not in VALID_OBJECTS:
            print(f"Invalid object: {object_name}")
            print("Allowed objects: cable, smartphone, feature phone")
            exit()

        if count<=0:
            print(f"Invalid count for {object_name}: {count}")
            exit()

        rows.append((object_name,count))

if not rows:
    print("No objects found in CSV.")
    exit()

cam=cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera could not be opened.")
    exit()

print("\nCamera started.")
print("Starting image capture...\n")

for row_index,(object_name,count) in enumerate(rows):

    if row_index>0:
        print("Changing object...")
        print("Waiting 10 seconds...")
        time.sleep(10)

    print("="*40)
    print(f"Object : {object_name}")
    print(f"Images : {count}")
    print("="*40)

    for image_count in range(1,count+1):

        ret,frame=cam.read()

        if not ret:
            print("Failed to capture image.")
            cam.release()
            exit()

        filename=os.path.join(
            SAVE_FOLDER,
            f"{object_name}_{image_count:02d}.jpg"
        )

        success=cv2.imwrite(filename,frame)

        if not success:
            print(f"Failed to save: {filename}")
            cam.release()
            exit()

        print(f"Saved [{image_count}/{count}]: {filename}")

        if image_count<count:
            time.sleep(2)

    print(f"Completed: {object_name}\n")

cam.release()

print("="*40)
print("ALL IMAGES CAPTURED SUCCESSFULLY")
print(f"Saved in: {SAVE_FOLDER}")
print("="*40)