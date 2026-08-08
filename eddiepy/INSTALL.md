# EddieLang 安裝方式

在 PowerShell 執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

安裝完成後，重新開啟 PowerShell 或 VS Code，再執行：

```powershell
eddie C:\路徑\你的程式.eddie
```

預設會安裝到：

```text
%LOCALAPPDATA%\EddieLang
```

也可以指定安裝位置：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -InstallDirectory "D:\Tools\EddieLang"
```
