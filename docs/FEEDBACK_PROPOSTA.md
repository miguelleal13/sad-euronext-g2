# Feedback dos professores à proposta e o que mudámos

| O que disseram | O que quer dizer | O que mudou no projeto |
|---|---|---|
| Tema muito original e boa estratégia por fases | A proposta foi bem recebida | — |
| Manter o livro de ordens de uma só ação e as interrupções como núcleo | O centro do trabalho é a Fase 1 | O núcleo não muda |
| **A Fase 1 sozinha já é um projeto completo: comprometam-se só com ela.** Alavancagem, brokers e contágio são extensões opcionais | Não vale a pena planear a Fase 2/3. Com tempo extra, melhora-se a Fase 1 | As tarefas da Fase 2 saíram dos guiões e foram substituídas por **análise de sensibilidade** (Margarida), **verificação** (Matilde) e **registo de pressupostos** (João) |
| **O livro de ordens vai ser sobretudo código Java: construam-no e testem-no primeiro** | O matching é lógica de programação, não blocos de arrastar | O livro passou a Java (`PriorityQueue` dentro do `Stock`; `Order` é uma classe Java). O Miguel faz **6 testes do livro antes de qualquer agente** (`testBook`) |
| **Verifiquem os limites da versão PLE do AnyLogic** | A versão gratuita tem limites (tamanho do modelo, número de agentes, experiências) | As ordens deixaram de ser agentes, porque milhões de ordens-agente arriscavam o limite. A experiência Optimization tem alternativa por Parameters Variation, caso a licença não a tenha |
| Os dados do livro e do comportamento dos investidores são escassos: **documentem os pressupostos** | Tudo o que é inventado tem de estar escrito e justificado | Novo [PRESSUPOSTOS.md](PRESSUPOSTOS.md), com dono, valor, fonte e teste |
| **Definam os factos estilizados antes de calibrar** | Fixar as metas primeiro e só depois afinar o modelo | Novo [FACTOS_ESTILIZADOS.md](FACTOS_ESTILIZADOS.md): 6 factos, métrica e critério, preenchidos na semana 1 |
| Validem estatísticas de **preço e volume**, mas **não digam que reproduzem crashes reais** | Comparar distribuições, não a história | Calibração com volume (`corr_volume_absret`, `autocorr_volume_lag1`). Os cenários passam a dizer “inspirado em BES / março 2020”; a validação do choque é só de plausibilidade |
