# Script para fazer commit e push das alterações
# Execute este script após adicionar o Git ao PATH ou usando GitHub Desktop

Write-Host "=== Script de Push para GitHub ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos em um repositório Git
if (-not (Test-Path .git)) {
    Write-Host "ERRO: Não é um repositório Git!" -ForegroundColor Red
    exit 1
}

# Verificar se o Git está disponível
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Git não está no PATH do sistema!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluções:" -ForegroundColor Yellow
    Write-Host "1. Adicione o Git ao PATH do Windows"
    Write-Host "2. Use o GitHub Desktop"
    Write-Host "3. Execute os comandos manualmente no terminal Git Bash"
    exit 1
}

Write-Host ""
Write-Host "Verificando status..." -ForegroundColor Cyan
git status

Write-Host ""
Write-Host "Adicionando todos os arquivos modificados..." -ForegroundColor Cyan
git add .

Write-Host ""
Write-Host "Fazendo commit..." -ForegroundColor Cyan
$commitMessage = "Tradução de nomes de funções, classes, atributos e parâmetros para português"
git commit -m $commitMessage

Write-Host ""
Write-Host "Fazendo push para origin/master..." -ForegroundColor Cyan
git push origin master

Write-Host ""
Write-Host "=== Push concluído com sucesso! ===" -ForegroundColor Green

