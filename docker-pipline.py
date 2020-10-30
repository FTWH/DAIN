# Cite Colab v1.5

INPUT_FILEPATH = "input.mp4" #@param{type:"string"}
OUTPUT_FILE_PATH = "output.mp4" #@param{type:"string"}
TARGET_FPS =  50 #@param{type:"number"}
FRAME_INPUT_DIR = '/content/DAIN/input_frames' #@param{type:"string"}
FRAME_OUTPUT_DIR = '/content/DAIN/output_frames' #@param{type:"string"}
START_FRAME = 1 #@param{type:"number"}
END_FRAME = -1 #@param{type:"number"}
SEAMLESS = False #@param{type:"boolean"}
RESIZE_HOTFIX = True #@param{type:"boolean"}
AUTO_REMOVE = True #@param{type:"boolean"}

# Detecting FPS of input file.
# Copy input.mp4
import os
os.system(f'cp -f /content/{INPUT_FILEPATH} /content/DAIN/')
filename = os.path.basename(INPUT_FILEPATH)
import cv2
cap = cv2.VideoCapture(f'/content/DAIN/{filename}')
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Input file has {fps} fps")

if(fps/TARGET_FPS>0.5):
  print("Define a higher fps, because there is not enough time for new frames. (Old FPS)/(New FPS) should be lower than 0.5. Interpolation will fail if you try.")

# ffmpeg extract - Generating individual frame PNGs from the source file.

os.system(f'rm -rf {FRAME_INPUT_DIR}') # %shell rm -rf '{FRAME_INPUT_DIR}'
os.system(f'mkdir -p {FRAME_INPUT_DIR}') # %shell mkdir -p '{FRAME_INPUT_DIR}'

if (END_FRAME==-1):
  os.system(f"ffmpeg -i /content/DAIN/{filename} -vf '" + f"select=gte(n\,{START_FRAME}),setpts=PTS-STARTPTS' " + f'{FRAME_INPUT_DIR}/%05d.png') 
else:
  os.system(f"ffmpeg -i /content/DAIN/{filename} -vf '" +f"select=between(n\,{START_FRAME}\,{END_FRAME}),setpts=PTS-STARTPTS' " + f'{FRAME_INPUT_DIR}/%05d.png') 

png_generated_count_command_result = os.popen(f'ls {FRAME_INPUT_DIR} | wc -l').read().strip()
frame_count = int(png_generated_count_command_result)

import shutil
if SEAMLESS:
  frame_count += 1
  first_frame = f"{FRAME_INPUT_DIR}/00001.png"
  new_last_frame = f"{FRAME_INPUT_DIR}/{frame_count.zfill(5)}.png"
  shutil.copyfile(first_frame, new_last_frame)

print(f"{frame_count} frame PNGs generated.")

# Checking if PNGs do have alpha
import subprocess as sp
os.chdir(f'{FRAME_INPUT_DIR}') 
channels = sp.getoutput('identify -format %[channels] 00001.png')
print (f"{channels} detected")

# Removing alpha if detected
if "a" in channels:
  print("Alpha channel detected and will be removed.")
  print(sp.getoutput('find . -name "*.png" -exec convert "{}" -alpha off PNG24:"{}" \;'))

# Interpolation
os.system(f'mkdir -p {FRAME_OUTPUT_DIR}') 
os.chdir('/content/DAIN') 

os.system(f'python -W ignore colab_interpolate.py --netName DAIN_slowmotion --time_step {fps/TARGET_FPS} --start_frame 1 --end_frame {frame_count} --frame_input_dir {FRAME_INPUT_DIR} --frame_output_dir {FRAME_OUTPUT_DIR}')

# Finding DAIN Frames, upscaling and cropping to match original
os.chdir(f'{FRAME_OUTPUT_DIR}') 

if (RESIZE_HOTFIX):
  images = []
  for filename in os.listdir(FRAME_OUTPUT_DIR):
    img = cv2.imread(os.path.join(FRAME_OUTPUT_DIR, filename))
    filename = os.path.splitext(filename)[0]
    if(not filename.endswith('0')):
      dimensions = (img.shape[1]+2, img.shape[0]+2)
      resized = cv2.resize(img, dimensions, interpolation=cv2.INTER_LANCZOS4)
      crop = resized[1:(dimensions[1]-1), 1:(dimensions[0]-1)]
      cv2.imwrite(f"{filename}.png", crop)

os.chdir(f'{FRAME_OUTPUT_DIR}') 
filename = os.path.basename(INPUT_FILEPATH)
os.system(f'ffmpeg -i /content/DAIN/{filename} -acodec copy output-audio.aac') 
os.system(f'ffmpeg -y -r {TARGET_FPS} -f image2 -pattern_type glob -i *.png -i output-audio.aac -shortest /content/{OUTPUT_FILE_PATH}') 

if (AUTO_REMOVE):
  os.system(f'rm -rf {FRAME_OUTPUT_DIR}/*')
  os.system('rm -rf output-audio.aac')