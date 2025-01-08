$scriptPath = ""
$suffixToRename = "fix"
$fileNames = Get-ChildItem -Path $scriptPath -Recurse -Include *$suffixToRename.csv
foreach($file in $fileNames) {
    $newName = $file.FullName -replace "_$suffixToRename", ""
    Move-Item -Force $file.FullName $newName
}
foreach($file in $fileNames) {
   Write-Output $file
}


