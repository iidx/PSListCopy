<###
Enter the paths separated by newlines here
###>
            $inc = 0;
            $csv_list = @(
                '"No","Path","Name","Extension","Size","Type","Owner","Group","Hidden","System","Encrypted","Compressed","Archive","Readable","Writable","Access Mask","Last Modified Time","Last Accessed Time","Created Time","Manufacturer","Version"'
            );
            $data = [regex]::match(
                        (Get-Content $PSCommandPath -Encoding UTF8 -Raw), 
                        '(?ms)<\#{3}\W(.+?\W)#{3}\>'
                    )[0].Groups[1].Value      
            foreach(
                $fn in $data.Split(
                            [Environment]::NewLine, 
                            [StringSplitOptions]::RemoveEmptyEntries
                        )
            ){
                $inc += 1;
                $f = $fn.Replace('\', '\\');
                try{
                    $owner = '"' + (get-acl $f).Owner + '"'
                } catch{
                    <#
                        Mostly, the exception is due to a problem with access permission to the domain.
                        You can check the exception message with the following command.
                        $_.Exception.GetType().FullName.toString()
                    #>
                    $owner = '"Unknown"'
                }
                try{
                    $group = '"' + (get-acl $f).Group + '"'
                } catch{
                    $group = '"Unknown"'
                }    
                try{
                    $f = (get-wmiobject -query ('select * from CIM_DataFile where name="{0}"' -f  $f))
                } catch{
                    $f = '"' + $_.Exception.GetType().FullName.toString() + '"'
                }
                $mac_datetimes = @(3);        
                foreach($o in @($f.lastmodified, $f.lastaccessed, $f.installdate) ){
                    try{
                        $_dt = [Management.ManagementDateTimeConverter]::ToDateTime($o)
                        $_dt = '"' + $_dt.ToString('yyyy-MM-dd hh:mm:ss') + '"'
                    } catch{
                        $_dt = '"Unknown"'
                    } finally{
                        $mac_datetimes += @($_dt);
                    }
                }
                $fn = '"'   + $fn + '"'
                $out = '"'  + $inc.toString() + '",' `
                            + $fn + ',' `
                            + $f.filename + '.' + $f.extension + ',' `
                            + $f.extension + ',' `
                            + $f.filesize + ',' `
                            + $f.filetype + ',' `
                            + $owner + ',' `
                            + $group + ',' `
                            + $f.hidden + ',' `
                            + $f.system + ',' `
                            + $f.encrypted + ',' `
                            + $f.compressed + ',' `
                            + $f.archive + ',' `
                            + $f.readable + ',' `
                            + $f.writeable + ',' `
                            + $f.accessmask + ',' `
                            + $mac_datetimes[1] + ',' `
                            + $mac_datetimes[2] + ',' `
                            + $mac_datetimes[3] + ',' `
                            + $f.manufacturer + ',' `
                            + $f.version
                $csv_list += @($out)
            }
            $csv_data = $csv_list -join "`n"
            Out-File -FilePath .\PSListCopy_Output.csv -InputObject $csv_data -Encoding 'UTF8'
        echo($PSCommandPath);