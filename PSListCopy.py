import os
import datetime
import argparse


class PSListCopy:
    def __init__(self, list_file, output, no_copy_flag, encoding='utf-8'):
        self.output = output
        self.encoding = encoding
        self.list_file = list_file
        self.no_copy_flag = no_copy_flag
    
    def run(self):
        paths = "\n".join(
            [path for path in self.load_list()]
        )
        script_data = f"<###\n{paths}\n###>{self._get_ps_script()}"
        if not self.no_copy_flag:
            script_data += self._copy_files()
        self._save_ps_file(script_data)
           

    def load_list(self):
        with open(self.list_file, 'r', encoding=self.encoding) as f:
            for path in f.readlines():
                yield path.strip()

    def _save_ps_file(self, script):
        with open(".\\PSListCopyRun.ps1", "w", encoding=self.encoding) as f:
            f.write(script)

    def _copy_files(self):
        xcopy_cmds = ["\n"]
        for path in self.load_list():
            trc_drive_letter = path.replace(':', '_DRIVE')
            dst_path = self.output + os.sep + trc_drive_letter
            command = f"xcopy /k/h/o/x/y \"{path}\" \"{dst_path}*\""
            xcopy_cmds.append(command)
        return "\n".join(xcopy_cmds)

    def _get_ps_script(self):
        # This is a Powershell script to get information about files
        script = """
            $inc = 0;
            $csv_list = @(
                \'\"No\",\"Full Path\",\"Name\",\"Extension\",\"Type\",\"Size\",\"Last Modified Time\",\"Last Accessed Time\",\"Created Time\",\"Owner\",\"Group\",\"Hidden\",\"System\",\"Encrypted\",\"Compressed\",\"Archive\",\"Readable\",\"Writable\",\"Access Mask\",\"Manufacturer\",\"Version\"\'
            );
            $data = [regex]::match(
                        (Get-Content $PSCommandPath -Encoding UTF8 -Raw), 
                        \'(?ms)<\#{3}\W(.+?\W)#{3}\>\'
                    )[0].Groups[1].Value      
            foreach(
                $fn in $data.Split(
                            [Environment]::NewLine, 
                            [StringSplitOptions]::RemoveEmptyEntries
                        )
            ){
                $inc += 1;
                $f = $fn.Replace(\'\\\', \'\\\\\');
                try{
                    $owner = \'\"\' + (get-acl $f).Owner + \'\"\'
                } catch{
                    <#
                        Mostly, the exception is due to a problem with access permission to the domain.
                        You can check the exception message with the following command.
                        $_.Exception.GetType().FullName.toString()
                    #>
                    $owner = \'\"Unknown\"\'
                }
                try{
                    $group = \'\"\' + (get-acl $f).Group + \'\"\'
                } catch{
                    $group = \'\"Unknown\"\'
                }    
                try{
                    $f = (get-wmiobject -query (\'select * from CIM_DataFile where name=\"{0}\"\' -f  $f))
                } catch{
                    $f = \'\"\' + $_.Exception.GetType().FullName.toString() + \'\"\'
                }
                $mac_datetimes = @(3);        
                foreach($o in @($f.lastmodified, $f.lastaccessed, $f.installdate) ){
                    try{
                        $_dt = [Management.ManagementDateTimeConverter]::ToDateTime($o)
                        $_dt = \'\"\' + $_dt.ToString(\'yyyy-MM-dd hh:mm:ss\') + \'\"\'
                    } catch{
                        $_dt = \'\"Unknown\"\'
                    } finally{
                        $mac_datetimes += @($_dt);
                    }
                }
                $fn = \'\"\'   + $fn + \'\"\'
                $out = \'\"\'  + $inc.toString() + \'\",\' `
                            + $fn + \',\' `
                            + $f.filename + \'.\' + $f.extension + \',\' `
                            + $f.extension + \',\' `
                            + $f.filetype + \',\' `
                            + $f.filesize + \',\' `
                            + $mac_datetimes[1] + \',\' `
                            + $mac_datetimes[2] + \',\' `
                            + $mac_datetimes[3] + \',\' `
                            + $owner + \',\' `
                            + $group + \',\' `
                            + $f.hidden + \',\' `
                            + $f.system + \',\' `
                            + $f.encrypted + \',\' `
                            + $f.compressed + \',\' `
                            + $f.archive + \',\' `
                            + $f.readable + \',\' `
                            + $f.writeable + \',\' `
                            + $f.accessmask + \',\' `
                            + $f.manufacturer + \',\' `
                            + $f.version
                $csv_list += @($out)
            }
            $csv_data = $csv_list -join \"`n\"
        """
        script += f"\nNew-Item -ItemType directory -Path .\{self.output}\n"
        script += f"Out-File -FilePath .\{self.output}\PSListCopy_Output.csv -InputObject $csv_data -Encoding \'UTF8\'"
        return script

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        PSListCopy is a script that can extract owner information and 
        datetime information for a list of files in a live response environment.
        """
    )
    parser.add_argument(
        '-l', '--list_file', 
        help='List of file separated by \\n', 
        required=True,
        dest="list_file_path"
    )
    parser.add_argument(
        '-o', '--output_path', 
        help='Path of output ps1 file', 
        default=f".\\PSListCopy_{int(datetime.datetime.now().timestamp())}\\",
        dest="out_path"
    )
    parser.add_argument(
        '-n', '--no_copy', 
        help='Saves only metadata about the file to csv(It does not acquisition files).', 
        default=False,
        action='store_true',
        dest="no_copy"
    )
    args = parser.parse_args()
    
    pslistcopy = PSListCopy(
        list_file=args.list_file_path,
        output=args.out_path,
        no_copy_flag=args.no_copy
    )
    pslistcopy.run()
    print("[+] Done.")
