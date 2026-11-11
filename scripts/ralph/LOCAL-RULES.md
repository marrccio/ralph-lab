

---

# REGRAS LOCAIS DESTE PROJETO (ia-3.1). Adicionadas pelo aluno; não fazem parte do upstream.

Estas regras valem acima de qualquer coisa que o texto anterior sugira.

- O projeto é em **Python**. Onde o texto acima fala em "typecheck", rode `python -m pytest -q`. Não existe typecheck, lint nem navegador neste projeto: no relatório, diga que a verificação em navegador não foi feita.
- Trabalhe **somente dentro deste repositório**. Não leia nem escreva fora dele. Não use a rede. **Nunca** faça `git push`, nunca use `gh`, não crie nem altere remotos nem a configuração do Git.
- Comandos permitidos: `python pipeline.py`, `python -m pytest`, `git add`, `git commit`, `git status`, `git diff`, `git log`, `git branch`, `git checkout`, `git switch`, `ls`, `cat`, `mkdir`, `date`. Qualquer outro comando será negado.
- **Nunca modifique `vendas.csv` nem `lojas.csv`** (dados de origem) e nunca apague linhas deles.
- Use apenas a **biblioteca padrão do Python** e o **pytest**. Sem pandas, sem CDN, sem JavaScript ou CSS externos.
- O pipeline fica em `pipeline.py` na raiz e é executado com `python pipeline.py`. Ele gera `vendas_lojas.csv`, `pivot_receita.csv`, `anomalias.md` e `index.html`.
- Se uma história não puder ser concluída, diga isso no `progress.txt` em vez de enfraquecer um teste. Não invente dados.
- Os commits devem ser feitos com a identidade que já está configurada no repositório. Não altere essa identidade.
- Se a história falhar em um critério, **não** marque `passes: true`.
