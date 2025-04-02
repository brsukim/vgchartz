# VGChartz Data Analysis Project

## Group Members:
 - Simon Ambrozak
 - Shubham Bhatnagar
 - Brandon Kim
 - Meherzan Gai
 - Jude Lwin

https://github.com/NewbieIndieGameDev/steam-insights
### How to get .csv files:
In the directory that THIS vgchartzs folder is in: (Ex: CS-Projects/)
```
git clone git@github.com:NewbieIndieGameDev/steam-insights.git
cd steam-insights
find . -name "*.zip" -exec unzip {} \;
find . -name "*.csv" -exec cp {} ../vgchartz/ \;
cd ../vgchartz/
```

### If on windows (on powershell):
```
git clone git@github.com:NewbieIndieGameDev/steam-insights.git
cd steam-insights
Get-ChildItem -Path . -Filter "*.zip" -Recurse | ForEach-Object { Expand-Archive -Path $_.FullName -DestinationPath (Split-Path -Path $_.FullName) }
$destination = "..\vgchartz\"
Get-ChildItem -Path . -Filter "*.csv" -Recurse | ForEach-Object { Copy-Item -Path $_.FullName -Destination $destination }

Set-Location -Path $destination
```
