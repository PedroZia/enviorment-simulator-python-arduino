# Roteiro — Como um robô aprende?

**Feira de Ciências 2026 · versão principal de 7 minutos**

Este roteiro acompanha o deck “Como um robô aprende?”. A fala foi escrita para ser dita, não lida: frases curtas, uma ideia por slide e pausas para olhar o robô. Os tempos são uma referência; se o público estiver envolvido, deixe a conversa correr e corte o que for menos importante. Os slides 14–16 e o apêndice ficam para perguntas.

## Roteiro principal — 7 minutos

| Slide | Tempo | Ideia-chave |
|---|---|---|
| 01 | 0:00–0:25 | Capa e gancho: “ele aprendeu sozinho” |
| 02 | 0:25–1:00 | O desafio: 3 sensores, 3 ações, 10 decisões/s |
| 03 | 1:00–1:35 | Duas abordagens: regras prontas × aprender fazendo |
| 04 | 1:35–2:10 | A recompensa: +1, −0,5, −3 |
| 05 | 2:10–2:40 | Os 8 estados: 2³ |
| 06 | 2:40–3:30 | A Q-table: 8 × 3 = 24 notas |
| 07 | 3:30–3:55 | A evolução: a tabela ganhando preferência |
| 08 | 3:55–4:20 | O ciclo: sensar, escolher, agir, medir |
| 09 | 4:20–4:50 | Explorar × confiar: ε de 1,00 a 0,13 |
| 10 | 4:50–5:20 | O treinamento: 200 episódios |
| 11 | 5:20–5:50 | O resultado: −49 → +559 |
| 12 | 5:50–6:15 | O comportamento: 5 → 120 passos |
| 13 | 6:15–6:35 | A curva não é lisa |
| 17 | 6:35–7:00 | Fechamento e demo ao vivo |

## Slide 01 · Capa — 0:00–0:25

**Fala**

Olá! Este é um robô seguidor de linha. A diferença é que ele não foi programado com todas as regras: ele aprendeu sozinho a seguir a linha.

A pergunta que guia o projeto é simples: como uma máquina aprende? Em sete minutos, eu vou mostrar o caminho. E o robô está aqui do lado, então no final vocês podem vê-lo rodando.

> **Ação:** Aponte para o robô na mesa. Deixe a pista visível, mas ainda sem ligar o robô.

## Slide 02 · O desafio — 0:25–1:00

**Fala**

Para a gente, seguir uma linha é quase automático. Olhamos, corrigimos o corpo e seguimos. Para uma máquina, cada instante é uma decisão.

Ele tem três sensores embaixo, dois motores e um Arduino. Dez vezes por segundo, ele precisa responder: para onde eu vou agora? Esquerda, reto ou direita? E ele não vê a linha: só sabe se cada sensor está no branco ou no preto.

> **Ação:** Aponte para os três sensores e para as rodas. Mostre o robô parado sobre a linha.

## Slide 03 · Duas abordagens — 1:00–1:35

**Fala**

Existem dois jeitos de resolver isso. No primeiro, o programador escreve todas as regras: se o sensor da esquerda vê preto e o da direita não, vire à esquerda. Funciona muito bem... até a pista mudar.

No segundo, o robô testa, recebe uma nota e ajusta o próprio comportamento. É aprendizado por reforço. O primeiro repete; o segundo se adapta. É esse segundo que a gente vai destrinchar.

> **Ação:** Gesto para a coluna da esquerda e depois para a da direita.

## Slide 04 · A recompensa — 1:35–2:10

**Fala**

O professor do robô não é uma pessoa: é a recompensa. Depois de cada ação, ele recebe uma nota. Se o sensor central está na linha, ganha +1. Se um sensor lateral está ativo, perde 0,5. Se perdeu a linha completamente, perde 3.

As notas se somam. É como treinar um cachorro com petiscos — só que o petisco aqui é um número. Ele não sabe o que é “certo”; ele aprende o que dá nota melhor.

> **Ação:** Aponte para os três números. Se houver visitantes, pergunte: “qual dessas notas vocês querem ganhar?”

## Slide 05 · Os 8 estados — 2:10–2:40

**Fala**

Para decidir, ele precisa resumir o mundo. Cada sensor só responde 0 ou 1: branco ou preto. Três sensores binários dão 2³, ou seja, 8 combinações.

Por exemplo: 010 quer dizer esquerda branco, centro preto, direita branco. Isso é o estado “centralizado”. Toda a percepção do robô cabe em oito códigos. É uma simplificação — e é isso que torna o problema tratável.

> **Ação:** Aponte para a linha 010 destacada e para os três pontos.

## Slide 06 · A Q-table — 2:40–3:30

**Fala**

Agora o coração do projeto: a Q-table. Ela tem oito linhas, uma para cada situação, e três colunas, uma para cada ação. Cada célula guarda uma nota: quanto vale aquela ação naquela situação.

Olha a linha 010, a situação centralizada: +7,7 para esquerda, +9,0 para reto, +8,3 para direita. A maior nota é 9,0, então ele escolhe reto. A célula terracota mostra a melhor ação de cada linha.

São 24 números. É só isso que ele precisa guardar. E repare na linha 000: todas as notas são negativas porque ele perdeu a linha. Ele ainda escolhe a menos ruim, mas aprende a evitar chegar ali.

> **Ação:** Passe o dedo na linha 010; depois aponte para a coluna RETO e para a célula terracota. Faça uma pausa de 2 segundos antes de dizer “24 números”.

## Slide 07 · A evolução da tabela — 3:30–3:55

**Fala**

E de onde vêm esses números? Do treinamento. No começo, a tabela está toda zerada. A cada episódio, ele erra, recebe a nota e atualiza uma célula.

Aqui estão quatro momentos: episódio 10, 50, 100 e 200. No começo, quase tudo neutro; no fim, cada linha já tem uma preferência clara. Não é um salto: é acumulação. Cada erro muda um pouquinho.

> **Ação:** Aponte para os quatro quadros, da esquerda para a direita.

## Slide 08 · O ciclo — 3:55–4:20

**Fala**

O ciclo é sempre o mesmo: sensar, escolher, agir, medir. Ele lê os três sensores, consulta a linha da tabela, aciona os motores e recebe a recompensa. Dez vezes por segundo.

A cada volta, uma única célula da tabela é atualizada. É um loop muito simples — e é isso que cabe dentro de um Arduino.

> **Ação:** Faça um círculo no ar acompanhando as setas.

## Slide 09 · Explorar × confiar — 4:20–4:50

**Fala**

Existe um dilema: ele pode repetir o que já sabe ou arriscar algo novo. No começo, ele chuta quase tudo: a exploração é 1,00, 100%. A cada episódio, essa curiosidade cai.

Depois de 200 episódios, está em 0,13: 13% de exploração, 87% de confiança no que aprendeu. O mínimo no código é 2%. Se só chutar, nunca aprende; se só repetir, nunca descobre algo melhor.

> **Ação:** Aponte para a curva e depois para os dois números.

## Slide 10 · O treinamento — 4:50–5:20

**Fala**

O treinamento acontece no simulador: 200 episódios, até 1.000 passos cada. Cada episódio começa em um ponto diferente da pista. Se ele fica 15 passos fora da linha, o episódio acaba.

No simulador, errar é barato: ele pode cair, sair da pista, recomeçar. Depois, a mesma tabela vai para o robô de verdade. Aqui, cada ponto é um episódio; os terracota são os snapshots que a gente usou para acompanhar a evolução.

> **Ação:** Aponte para o número 200, depois para a grade de pontos.

## Slide 11 · O resultado — 5:20–5:50

**Fala**

E o resultado aparece na recompensa. Nos primeiros 20 episódios, a média era −49. Nos últimos 20, +559. Isso não é um prêmio: é o sinal de que ele passa muito mais tempo na linha.

A curva completa está no próximo slide. Mas o número grande resume: ele saiu de um comportamento ruim para um comportamento bom.

> **Ação:** Pause depois de “+559”. Deixe o número aparecer para o público.

## Slide 12 · O comportamento — 5:50–6:15

**Fala**

Para comparar, a mesma pista e o mesmo ponto de partida. Em cima, a política aleatória: ela fica na linha só 5 passos e sai. Embaixo, a política aprendida: 120 passos, 120 na linha.

Cada quadradinho é um passo; terracota quer dizer “está sobre a linha”. A diferença não é sorte: é a tabela.

> **Ação:** Aponte para a faixa de cima e depois para a de baixo. Se o robô estiver rodando, aponte para ele também.

## Slide 13 · A curva não é lisa — 6:15–6:35

**Fala**

Só que a curva não é lisa. Cada linha clara é um episódio; a linha escura é a média móvel. Tem queda, tem episódio ruim, tem variação.

O melhor episódio chegou a +822, mas os últimos 20 ficaram em +559. Aprender é irregular. Ele ainda erra — só erra menos.

> **Ação:** Não tente justificar cada queda. A mensagem é a tendência, não cada ponto.

## Slide 17 · Fechamento — 6:35–7:00

**Fala**

Então, voltando à pergunta do começo: como um robô aprende? Ele não nasceu sabendo. Ele tentou, errou, recebeu notas e ajustou uma tabela de 24 números. Isso é aprendizado por reforço.

E o robô está aqui do lado: eu posso colocá-lo na pista agora. Enquanto ele anda, reparem nos sensores e nas rodas. E me perguntem: e se a linha acabar? Obrigado!

> **Ação:** Coloque o robô na pista e deixe-o rodar por 10–15 segundos antes de abrir para perguntas.

## Versão estendida — acrescente os slides 14–16

Se sobrar tempo ou se a conversa pedir mais profundidade, insira estes três slides **depois do 13 e antes do 17**. O total fica em cerca de 9 minutos.

## Slide 14 · Arquitetura — +0:00–0:40

**Fala**

Se vocês quiserem entender como isso vira um projeto de engenharia, existem quatro formas de montar. A mais simples é o if/else, que é a linha de base. Depois, o simulador em Python, que treina rápido.

Depois, o agente embarcado no Arduino, que aprende sozinho. E o modo serial, em que o Python manda leituras e o Arduino devolve ações. A mesma tabela de 24 números pode viver no PC ou na RAM do microcontrolador. O robô aqui usa a versão embarcada.

> **Ação:** Aponte para as três colunas do slide: simulador, ponte e robô.

## Slide 15 · Por que importa — +0:40–1:10

**Fala**

Por que isso importa? Porque é inteligência artificial rodando local, sem nuvem, com 24 números e um microcontrolador barato. É a ideia de edge AI: decidir perto de onde a ação acontece.

E é uma forma muito concreta de ensinar reforço: dá para ver a tabela mudando.

> **Ação:** Sem pressa. Deixe a frase “sem nuvem” cair.

## Slide 16 · Limites — +1:10–1:40

**Fala**

E o que ele ainda não sabe? Oito estados é pouco para curvas fechadas e cruzamentos. A linha ainda pode ser perdida. E o simulador não é o chão de verdade: atrito, ruído e bateria mudam o jogo.

Os próximos passos são mais sensores, câmera e estados contínuos. O próximo passo é sair do discreto — e continuar aprendendo.

> **Ação:** Aponte para o “8 → ∞” e depois para a lista de próximos passos.

## Perguntas prováveis

**O que é Q-learning, em uma frase?**

É aprender por tentativa e erro: o robô age, recebe uma nota e guarda quanto vale cada ação em cada situação. Aqui, a “memória” é uma tabela de 8 por 3.

**Ele realmente aprende ou é só um monte de if/else?**

As regras de aprendizado são programadas; o comportamento, não. A tabela começa zerada e é preenchida pela experiência. O if/else decide sempre igual; o Q-learning muda com o que vive.

**Por que 8 estados?**

São 3 sensores binários: 2³ = 8. É uma simplificação deliberada. Com mais sensores ou câmera, o número de estados cresce — e o próximo passo é justamente esse.

**Por que a recompensa é negativa?**

Negativo é um sinal de “essa ação me afastou do objetivo”. O −3 é o pior caso: perdeu a linha. Ele aprende a evitar. O +1 é o centro na linha.

**Ele ainda erra?**

Sim. A curva não é lisa e a política final pode perder a linha em curvas fechadas ou pisos diferentes. O aprendizado reduz o erro; não elimina.

**Quanto tempo leva para treinar?**

No simulador, são 200 episódios, até 1.000 passos cada. No Arduino, o treinamento é online e mais lento, porque cada ação tem um delay de 100 ms. O tempo real depende da pista e do hardware.

**Por que não usar if/else?**

If/else é ótimo quando você conhece todas as situações. O aprendizado serve para adaptar quando a pista ou as condições mudam. O if/else é a linha de base.

**Isso é inteligência artificial de verdade?**

É uma forma clássica de aprendizado por reforço, não um modelo generativo. Mas é IA que aprende com experiência e toma decisão — e cabe em um microcontrolador.

**O que acontece se ele perder a linha?**

No simulador, 15 passos perdidos encerram o episódio. No robô real, ele pode parar ou continuar a última ação, dependendo do firmware. A recompensa −3 pune esse comportamento.

**Quanto custa e o que tem dentro?**

Arduino, três sensores IR, ponte H L298N, dois motores DC com caixa de redução, chassi e bateria. A Q-table ocupa 24 números na RAM; não precisa de nuvem nem de câmera.

**Dá para usar em carro autônomo?**

A ideia é a mesma, mas o espaço de estados é muito maior. Aqui é uma versão didática, embarcada e de baixo custo. É um ponto de partida, não um produto.

**O que é epsilon?**

É a chance de explorar: começa em 1,00 (100%) e cai para 0,13 em 200 episódios, com mínimo de 0,02. É o equilíbrio entre arriscar e confiar.

## Checklist antes da feira

- Ensaie com o robô ligado: fale enquanto ele anda.
- Teste a pista e a carga da bateria; leve bateria/pilhas reserva.
- Leve o PDF em um pendrive e também no e-mail/cloud.
- Teste HDMI, som e brilho; desative notificações.
- Imprima este roteiro ou deixe no celular; o deck tem notas, mas o papel é o backup.
- Deixe o robô em uma mesa segura e fixe a pista com fita.
- Leve um pano ou escova macia para limpar os sensores.
- Não deixe visitantes pegarem no robô; convide a apontar.
- Plano B: se o robô falhar, use os slides 11–12 e explique a tabela; se o projetor falhar, use o robô e este roteiro.

## Números para decorar

- **3** — sensores · 3 ações · 8 estados · 24 notas
- **200** — episódios · até 1.000 passos · 15 passos perdidos
- **−49 → +559** — recompensa média: primeiros 20 × últimos 20 episódios
- **5 → 120** — passos na linha: política aleatória × política aprendida
- **1,00 → 0,13** — exploração: início × após 200 episódios (mínimo 0,02)

## Frases de bolso

- “Ele não vê a linha; ele sente o contraste.”
- “A tabela é o cérebro dele.”
- “No começo ele chuta; depois confia.”
- “Aprender é irregular.”
- “Ele não nasceu sabendo. Aprendeu.”
