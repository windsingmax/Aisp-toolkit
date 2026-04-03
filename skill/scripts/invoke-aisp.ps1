#Requires -Version 5.1
<#
.SYNOPSIS
  代发 AIServiceProxy 请求；从本机私密文件读 API Key，避免把 Key 写进 Cursor/Claude 审批框里的 curl 命令行。

  一次性准备（在用户本机执行，勿把 Key 发给助手）：
  1. mkdir $HOME\.gbits -Force
  2. 将 Key 单行写入： $HOME\.gbits\aiserviceproxy_api_key.txt
  3. 仅当前用户可读（资源管理器 → 属性 → 安全）

  助手侧只应运行本脚本 + 参数，审批界面不应出现 asp_ 密钥。
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $Uri,
    [ValidateSet('GET', 'POST')]
    [string] $Method = 'GET',
    [string] $BodyPath = ''
)

$keyFile = Join-Path $env:USERPROFILE '.gbits\aiserviceproxy_api_key.txt'
if (-not (Test-Path -LiteralPath $keyFile)) {
    Write-Error "未找到密钥文件: $keyFile （请先按 SKILL.md 说明创建，勿在聊天里贴 Key）"
    exit 1
}

$key = (Get-Content -LiteralPath $keyFile -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Error "密钥文件为空: $keyFile"
    exit 1
}

if ($Method -eq 'POST') {
    if ([string]::IsNullOrWhiteSpace($BodyPath) -or -not (Test-Path -LiteralPath $BodyPath)) {
        Write-Error "POST 需要有效 -BodyPath 指向 JSON 文件"
        exit 1
    }
    & curl.exe -s -X POST $Uri `
        -H "Authorization: Bearer $key" `
        -H "Content-Type: application/json" `
        -d "@$BodyPath"
} else {
    & curl.exe -s $Uri -H "Authorization: Bearer $key"
}
