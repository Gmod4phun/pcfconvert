# pcfconvert source code

import os
import subprocess
from os import listdir
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

isdir = os.path.isdir
join = os.path.join

print('[pcfconvert] Source Engine Particle converter by Gmod4phun (steamcommunity.com/id/Gmod4phun)\n\n')
print('Purpose: Convert particles from newer Source Engine games to the GMod Source Engine version\n')
print('Requirements: Half-Life 2 and CS:GO Authoring Tools installed\n')
print('Usage: create a folder called "particles_src" in the same dir as the .exe, put your .pcf particle files in there, run the program and follow the instructions.')
print('The converted particles will be in a folder called "particles_dst"\n')

path = os.path.dirname(os.path.realpath(__file__))
print("Executable directory: "+path+"\n")

# set paths to csgo and hl2 bin folder
path_csgo = r'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\bin'
path_hl2 = r'C:\Program Files (x86)\Steam\steamapps\common\Half-Life 2\bin'

print("Default CSGO Bin directory: "+path_csgo+"\n")
isOK = input('Is the directory ok? type "y" for yes, "n" for no: ')

if isOK == "n":
    path_csgo = input("\nEnter CSGO Bin directory: ")

print("\nCSGO Bin directory: "+path_csgo+"\n")

if not os.path.isfile(join(path_csgo,"dmxconvert.exe")):
    input("Cannot find dmxconvert.exe, stopping, press ENTER to quit...\n")
    sys.exit(0)
print("Located dmxconvert.exe in CSGO directory, ok...\n")

print("Default HL2 Bin directory: "+path_hl2+"\n")
isOK = input('Is the directory ok? type "y" for yes, "n" for no: ')

if isOK == "n":
    path_hl2 = input("\nEnter HL2 Bin directory: ")

print("\nHL2 Bin directory: "+path_hl2+"\n")

if not os.path.isfile(join(path_hl2,"dmxconvert.exe")):
    input("Cannot find dmxconvert.exe, stopping, press ENTER to quit...\n")
    sys.exit(0)
print("Located dmxconvert.exe in HL2 directory, ok...\n")

input("Press ENTER to start the conversion\n")

# name of the source and destination folders for converting particles
srcfolder = 'particles_src'
dstfolder = 'particles_dst'

####
# you should not edit anything after this line
####

#textfile encoding:
ENCODING_TEXTFILE_ORIG = '<!-- dmx encoding keyvalues2 1 format tex 1 -->'
ENCODING_TEXTFILE_FIX = '<!-- dmx encoding keyvalues2 1 format pcf 1 -->'

#gmod pcf encoding
ENCODING_GMODPCF_ORIG = '<!-- dmx encoding binary 2 format dmx 1 -->'
ENCODING_GMODPCF_FIX = '<!-- dmx encoding binary 2 format pcf 1 -->'

path_src = join(path, srcfolder)
path_dst = join(path, dstfolder)

if not os.path.exists(path_dst):
    os.makedirs(path_dst)

def make_txt_from_pcf():
    for dirpath, dirnames, filenames in os.walk(path_src):
        for file in filenames:
            if ".pcf" in file:
                print("Processing: {} -> {}".format(file, file.split('.')[0]+".txt"))
                particle_name = os.path.splitext(file)[0]
                pcfname = join(dirpath, particle_name+".pcf")
                txtname = join(dirpath, particle_name+".txt")
                
                dmxconvert_params = 'dmxconvert -i "{}" -ie binary -o "{}" -of tex'.format(pcfname, txtname)
                
                toExec = join(path_csgo, dmxconvert_params)
                
                subprocess.call(toExec, shell=False)


def make_pcf_from_txt():
    for dirpath, dirnames, filenames in os.walk(path_src):
        for file in filenames:
            if ".txt" in file:
                print("Processing: {} -> {}".format(file, file.split('.')[0]+".pcf_temp"))
                particle_name = os.path.splitext(file)[0]
                txtname = join(dirpath, particle_name+".txt")
                newpcfname = join(path_dst, particle_name+".pcf_temp")
                
                dmxconvert_params = 'dmxconvert -i "{}" -ie tex -o "{}" -of binary'.format(txtname, newpcfname)
                
                toExec = join(path_hl2, dmxconvert_params)
                
                subprocess.call(toExec, shell=False)


def replace_line_in_file(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path, errors="ignore") as old_file:
            fixedfirst = False
            for line in old_file:
                if not fixedfirst:
                    line = line.replace(pattern, subst)
                    fixedfirst = True
                new_file.write(line)
    
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)


def fix_txt_encoding():
    for dirpath, dirnames, filenames in os.walk(path_src):
        for file in filenames:
            if ".txt" in file:
                print("Processing: "+file)
                txtfile = join(dirpath, file)

                replace_line_in_file(txtfile, ENCODING_TEXTFILE_ORIG, ENCODING_TEXTFILE_FIX)


def replace_dmx_with_pcf_binary(file): #we have to read in binary, and change dmx to pcf
    with open(file, "rb") as in_file, open(file.split('.')[0]+".pcf", "wb") as out_file:
        pos = 1
        while True:
            byte = in_file.read(1)
            if not byte:
                break
            
            if pos == 35:
                byte = b'p'
            if pos == 36:
                byte = b'c'
            if pos == 37:
                byte = b'f'
            
            out_file.write(byte)
            pos+=1


def fix_gmodpcf_encoding():
    for dirpath, dirnames, filenames in os.walk(path_dst):
        for file in filenames:
            if ".pcf_temp" in file:
                print("Processing: {} -> {}".format(file, file.split('.')[0]+".pcf"))
                txtfile = join(dirpath, file)

                replace_dmx_with_pcf_binary(txtfile)


def cleanup_temp_and_txt():
    for dirpath, dirnames, filenames in os.walk(path_src):
        for file in filenames:
            if ".txt" in file:
                toRemove = join(dirpath, file)
                os.remove(toRemove)
                
    for dirpath, dirnames, filenames in os.walk(path_dst):
        for file in filenames:
            if ".pcf_temp" in file:
                toRemove = join(dirpath, file)
                os.remove(toRemove)



#input("Press ENTER to start step 1: convert pcf to txt\n")
#make_txt_from_pcf()

#input("Press ENTER to start step 2: fix txt encoding\n")
fix_txt_encoding()

#input("Press ENTER to start step 3: convert txt to gmod pcf\n")
make_pcf_from_txt()

#input("Press ENTER to start step 4: fix gmod pcf encoding\n")
fix_gmodpcf_encoding()

shouldCleanup = input('Cleanup temporary .txt and .pcf_temp files? "y" for yes, "n" for no: ')
if shouldCleanup == "y":
    cleanup_temp_and_txt()

input("\nFinished! Press ENTER to exit...")
