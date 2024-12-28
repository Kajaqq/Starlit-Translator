$scriptPath = "pakchunk99-EngPatch"
$fileNames = Get-ChildItem -Path $scriptPath -Recurse -Include *fix.csv
foreach($file in $fileNames) {
    $newName = $file.FullName -replace "_fix", ""
    Move-Item -Force $file.FullName $newName
}
foreach($file in $fileNames) {
   Write-Output $file
}


