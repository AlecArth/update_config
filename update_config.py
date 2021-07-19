import os
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import time
import subprocess
import time
import argparse

def updateSeedNum(file_path, seed_file_path, newSeed=-1):
    print("updateSeedNum")
    seedNum = 0
    if newSeed == -1:
        seedNum = int(getCurrentSeed(seed_file_path))
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if line[:5] == "seed:":
                    if newSeed != -1:
                        seedNum = newSeed
                        updatedSeed = "seed: "+str(newSeed)+"\n"
                    else:
                        seedNum += 1
                        updatedSeed = "seed: "+str(seedNum)+"\n"
                    new_file.write(line.replace(line, updatedSeed))
                else:
                    new_file.write(line)
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    # Update seed save file.
    saveCurrentSeed(seed_file_path, seedNum)

def getCurrentSeed(seed_file_path):
    print("getCurrentSeed")
    if os.path.exists(seed_file_path):
        with open(seed_file_path) as file:
            first_line = file.readline()
        return first_line
    else:
        return 1000

def saveCurrentSeed(seed_file_path, seedNum):
    print("saveCurrentSeed")
    if os.path.exists(seed_file_path):

        file = open(seed_file_path, 'w')
        file.write(str(seedNum))
        file.close()
    else:
        file = open(seed_file_path, 'x')
        file.write("1000")
        file.close()

def threeRovers(file_path):
    updateRoverNumber(file_path, "  scouts: 2", "  scouts: 1")
    updateRoverNumber(file_path, "  excavators: 2", "  excavators: 1")
    updateRoverNumber(file_path, "  haulers: 2", "  haulers: 1")

def sixRovers(file_path):
    updateRoverNumber(file_path, "  scouts: 1", "  scouts: 2")
    updateRoverNumber(file_path, "  excavators: 1", "  excavators: 2")
    updateRoverNumber(file_path, "  haulers: 2", "  haulers: 2")

def updateRoverNumber(file_path, pattern, subst):
    print("updateRoverNumber")
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    copymode(file_path, abs_path)
    remove(file_path)
    move(abs_path, file_path)

def runPreCommands(cwd, pull, checkoutBranch=""):
    print("runPreCommands")
    subprocess.run(["clear"], cwd="competition-round/")
    time.sleep(1)
    os.system("cd "+cwd+" && make kill-all-containers")
    time.sleep(1)
    os.system("git -C "+cwd+" stash")
    time.sleep(1)
    if len(checkoutBranch) > 0:
        command = "git -C "+cwd+" checkout "+checkoutBranch
        os.system(command)
    time.sleep(1)
    if pull:
        os.system("git -C "+cwd+" pull")
        time.sleep(1)

def runCommands(cwd, init, build, extra_cpus, sim_no_gui):
    print("runCommands")
    if init:
        subprocess.run(["make", "init"], cwd=cwd)
        time.sleep(1)
    if build:
        subprocess.run(["make", "build-solution"], cwd=cwd)
        time.sleep(1)

    if sim_no_gui:
        subprocess.Popen(["make", "run-sim-no-gui"], cwd=cwd)
    else:
        subprocess.Popen(["make", "run-sim"], cwd=cwd)
    time.sleep(65)

    if extra_cpus:
        subprocess.run(["make", "run-solution-extra-cpus"], cwd=cwd)
    else:
        subprocess.run(["make", "run-solution"], cwd=cwd)
    # time.sleep(60)
    # subprocess.run(["make", "kill-all-containers"], cwd="competition-round/")
    # subprocess.run(["clear"], cwd="competition-round/")
    # time.sleep(1)
    # subprocess.Popen(["make", "run-sim"], cwd="competition-round/")
    # time.sleep(3)
    # subprocess.Popen(["gnome-terminal", "--tab-with-profile=a", "--", "make", "run-solution"], cwd="competition-round/")
    # os.system("cd competition-round/ && gnome-terminal --tab-with-profile=a -- make run-solution")
    # time.sleep(3)
    # subprocess.Popen(["gnome-terminal", "--tab-with-profile=a", "--", "make", "run-solution"], cwd="competition-round/")
    # os.system("cd competition-round/ && gnome-terminal --tab-with-profile=a -- make run-solution")

def runSimOnly(cwd):
    subprocess.run(["make", "kill-all-containers"], cwd=cwd)
    time.sleep(1)
    subprocess.run(["clear"], cwd=cwd)
    time.sleep(1)
    subprocess.Popen(["make", "run-sim"], cwd=cwd)
    time.sleep(65)
    subprocess.run(["make", "run-solution"], cwd=cwd)

def main():
    cwd = "../competition-round/"

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--branch', type=str, default="")
    parser.add_argument('--seed', type=int, default=-1)
    parser.add_argument('--file_path', type=str, default=cwd+"config.yml")
    parser.add_argument('--seed_file_path', type=str, default="seedNumber.txt")
    parser.add_argument('--numberOfRovers', type=int, default=6)
    parser.add_argument('--makeSimOnly', type=bool, default=False)
    parser.add_argument('--init', type=bool, default=False)
    parser.add_argument('--build', type=bool, default=False)
    parser.add_argument('--pull', type=bool, default=False)
    parser.add_argument('--extra_cpus', type=bool, default=False)
    parser.add_argument('--sim_no_gui', type=bool, default=False)
    args = parser.parse_args()
    print(args)

    checkoutBranch=args.branch
    newSeed=args.seed
    file_path = args.file_path
    seed_file_path = args.seed_file_path
    numberOfRovers = args.numberOfRovers
    makeSimOnly = args.makeSimOnly
    init = args.init
    build = args.build
    pull = args.pull
    extra_cpus = args.extra_cpus
    sim_no_gui = args.sim_no_gui
    
    if makeSimOnly:
        runSimOnly(cwd)
    else:
        runPreCommands(cwd, pull, checkoutBranch)

        updateSeedNum(file_path, seed_file_path, newSeed)

        if numberOfRovers == 3:
            threeRovers(file_path)
        else:
            sixRovers(file_path)

        runCommands(cwd, init, build, extra_cpus, sim_no_gui)


if __name__ == "__main__":
    main()
