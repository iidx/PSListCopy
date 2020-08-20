# PSListCopy
File and file meta information acquisition using PowerShell in Live Response environment.
![](/img/pslistcopy.png)

## Requirements
- ```Python 3.8+```

## Usage
1. First, prepare a list of files to be collected from the Victim PC, such as ```tests\sample.txt```.
2. Create a PowerShell script with the following command.
    - When collecting both files and metadata: ```python PSListCopy.py -l files.txt```
    - When collecting only metadata: ```python PSListCopy.py -l files.txt -n```
3. Move the PowerShell script(```PSListCopy.ps1```) to Victim PC.
4. Run PowerShell as administrator on Victim PC.
5. Enter the ```Set-ExecutionPolicy Unrestricted``` command to temporarily change the script execution policy.
6. Run ```PSListCopy.ps1```
