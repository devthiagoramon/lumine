# Comandos Git para Push

Como o Git não está no PATH do sistema, você pode executar os seguintes comandos manualmente:

## Opção 1: Usar Git Bash (se instalado)
Abra o Git Bash e execute:

```bash
cd C:\Programacao\MPS\lumine
git status
git add .
git commit -m "Tradução de nomes de funções, classes, atributos e parâmetros para português"
git push origin master
```

## Opção 2: Usar GitHub Desktop
1. Abra o GitHub Desktop
2. O repositório deve aparecer automaticamente
3. Revise as alterações
4. Adicione uma mensagem de commit: "Tradução de nomes de funções, classes, atributos e parâmetros para português"
5. Clique em "Commit to master"
6. Clique em "Push origin"

## Opção 3: Adicionar Git ao PATH
1. Encontre onde o Git está instalado (geralmente `C:\Program Files\Git\bin`)
2. Adicione ao PATH do Windows:
   - Painel de Controle > Sistema > Configurações Avançadas do Sistema
   - Variáveis de Ambiente > Path > Editar
   - Adicione o caminho do Git
3. Reinicie o terminal e execute o script `git_push.ps1`

## Resumo das Alterações
- ✅ Models traduzidos (parâmetros de funções)
- ✅ Controllers traduzidos (variáveis e parâmetros)
- ✅ Schemas mantidos em inglês (compatibilidade com frontend)


