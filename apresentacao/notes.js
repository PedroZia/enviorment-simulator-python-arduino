module.exports = {
  "01": `SLIDE 01 · CAPA · 0:00–0:25

FALA
Olá! Este é um robô seguidor de linha. A diferença é que ele não foi programado com todas as regras: ele aprendeu sozinho a seguir a linha.
A pergunta que guia o projeto é simples: como uma máquina aprende? Em sete minutos, eu vou mostrar o caminho. E o robô está aqui do lado, então no final vocês podem vê-lo rodando.

AÇÃO
Aponte para o robô na mesa. Deixe a pista visível, mas ainda sem ligar o robô.`,

  "02": `SLIDE 02 · O DESAFIO · 0:25–1:00

FALA
Para a gente, seguir uma linha é quase automático. Olhamos, corrigimos o corpo e seguimos. Para uma máquina, cada instante é uma decisão.
Ele tem três sensores embaixo, dois motores e um Arduino. Dez vezes por segundo, ele precisa responder: para onde eu vou agora? Esquerda, reto ou direita? E ele não vê a linha: só sabe se cada sensor está no branco ou no preto.

AÇÃO
Aponte para os três sensores e para as rodas. Mostre o robô parado sobre a linha.`,

  "03": `SLIDE 03 · DUAS ABORDAGENS · 1:00–1:35

FALA
Existem dois jeitos de resolver isso. No primeiro, o programador escreve todas as regras: se o sensor da esquerda vê preto e o da direita não, vire à esquerda. Funciona muito bem... até a pista mudar.
No segundo, o robô testa, recebe uma nota e ajusta o próprio comportamento. É aprendizado por reforço. O primeiro repete; o segundo se adapta. É esse segundo que a gente vai destrinchar.

AÇÃO
Gesto para a coluna da esquerda e depois para a da direita.`,

  "04": `SLIDE 04 · A RECOMPENSA · 1:35–2:10

FALA
O professor do robô não é uma pessoa: é a recompensa. Depois de cada ação, ele recebe uma nota. Se o sensor central está na linha, ganha +1. Se um sensor lateral está ativo, perde 0,5. Se perdeu a linha completamente, perde 3.
As notas se somam. É como treinar um cachorro com petiscos — só que o petisco aqui é um número. Ele não sabe o que é “certo”; ele aprende o que dá nota melhor.

AÇÃO
Aponte para os três números. Se houver visitantes, pergunte: “qual dessas notas vocês querem ganhar?”`,

  "05": `SLIDE 05 · OS 8 ESTADOS · 2:10–2:40

FALA
Para decidir, ele precisa resumir o mundo. Cada sensor só responde 0 ou 1: branco ou preto. Três sensores binários dão 2³, ou seja, 8 combinações.
Por exemplo: 010 quer dizer esquerda branco, centro preto, direita branco. Isso é o estado “centralizado”. Toda a percepção do robô cabe em oito códigos. É uma simplificação — e é isso que torna o problema tratável.

AÇÃO
Aponte para a linha 010 destacada e para os três pontos.`,

  "06": `SLIDE 06 · A Q-TABLE · 2:40–3:30

FALA
Agora o coração do projeto: a Q-table. Ela tem oito linhas, uma para cada situação, e três colunas, uma para cada ação. Cada célula guarda uma nota: quanto vale aquela ação naquela situação.
Olha a linha 010, a situação centralizada: +7,7 para esquerda, +9,0 para reto, +8,3 para direita. A maior nota é 9,0, então ele escolhe reto. A célula terracota mostra a melhor ação de cada linha.
São 24 números. É só isso que ele precisa guardar. E repare na linha 000: todas as notas são negativas porque ele perdeu a linha. Ele ainda escolhe a menos ruim, mas aprende a evitar chegar ali.

AÇÃO
Passe o dedo na linha 010; depois aponte para a coluna RETO e para a célula terracota. Faça uma pausa de 2 segundos antes de dizer “24 números”.`,

  "07": `SLIDE 07 · A EVOLUÇÃO DA TABELA · 3:30–3:55

FALA
E de onde vêm esses números? Do treinamento. No começo, a tabela está toda zerada. A cada episódio, ele erra, recebe a nota e atualiza uma célula.
Aqui estão quatro momentos: episódio 10, 50, 100 e 200. No começo, quase tudo neutro; no fim, cada linha já tem uma preferência clara. Não é um salto: é acumulação. Cada erro muda um pouquinho.

AÇÃO
Aponte para os quatro quadros, da esquerda para a direita.`,

  "08": `SLIDE 08 · O CICLO · 3:55–4:20

FALA
O ciclo é sempre o mesmo: sensar, escolher, agir, medir. Ele lê os três sensores, consulta a linha da tabela, aciona os motores e recebe a recompensa. Dez vezes por segundo.
A cada volta, uma única célula da tabela é atualizada. É um loop muito simples — e é isso que cabe dentro de um Arduino.

AÇÃO
Faça um círculo no ar acompanhando as setas.`,

  "09": `SLIDE 09 · EXPLORAR × CONFIAR · 4:20–4:50

FALA
Existe um dilema: ele pode repetir o que já sabe ou arriscar algo novo. No começo, ele chuta quase tudo: a exploração é 1,00, 100%. A cada episódio, essa curiosidade cai.
Depois de 200 episódios, está em 0,13: 13% de exploração, 87% de confiança no que aprendeu. O mínimo no código é 2%. Se só chutar, nunca aprende; se só repetir, nunca descobre algo melhor.

AÇÃO
Aponte para a curva e depois para os dois números.`,

  "10": `SLIDE 10 · O TREINAMENTO · 4:50–5:20

FALA
O treinamento acontece no simulador: 200 episódios, até 1.000 passos cada. Cada episódio começa em um ponto diferente da pista. Se ele fica 15 passos fora da linha, o episódio acaba.
No simulador, errar é barato: ele pode cair, sair da pista, recomeçar. Depois, a mesma tabela vai para o robô de verdade. Aqui, cada ponto é um episódio; os terracota são os snapshots que a gente usou para acompanhar a evolução.

AÇÃO
Aponte para o número 200, depois para a grade de pontos.`,

  "11": `SLIDE 11 · O RESULTADO · 5:20–5:50

FALA
E o resultado aparece na recompensa. Nos primeiros 20 episódios, a média era −49. Nos últimos 20, +559. Isso não é um prêmio: é o sinal de que ele passa muito mais tempo na linha.
A curva completa está no próximo slide. Mas o número grande resume: ele saiu de um comportamento ruim para um comportamento bom.

AÇÃO
Pause depois de “+559”. Deixe o número aparecer para o público.`,

  "12": `SLIDE 12 · O COMPORTAMENTO · 5:50–6:15

FALA
Para comparar, a mesma pista e o mesmo ponto de partida. Em cima, a política aleatória: ela fica na linha só 5 passos e sai. Embaixo, a política aprendida: 120 passos, 120 na linha.
Cada quadradinho é um passo; terracota quer dizer “está sobre a linha”. A diferença não é sorte: é a tabela.

AÇÃO
Aponte para a faixa de cima e depois para a de baixo. Se o robô estiver rodando, aponte para ele também.`,

  "13": `SLIDE 13 · A CURVA NÃO É LISA · 6:15–6:35

FALA
Só que a curva não é lisa. Cada linha clara é um episódio; a linha escura é a média móvel. Tem queda, tem episódio ruim, tem variação.
O melhor episódio chegou a +822, mas os últimos 20 ficaram em +559. Aprender é irregular. Ele ainda erra — só erra menos.

AÇÃO
Não tente justificar cada queda. A mensagem é a tendência, não cada ponto.`,

  "14": `SLIDE 14 · ARQUITETURA · VERSÃO ESTENDIDA (+0:00–0:40)

FALA
Se vocês quiserem entender como isso vira um projeto de engenharia, existem quatro formas de montar. A mais simples é o if/else, que é a linha de base. Depois, o simulador em Python, que treina rápido.
Depois, o agente embarcado no Arduino, que aprende sozinho. E o modo serial, em que o Python manda leituras e o Arduino devolve ações. A mesma tabela de 24 números pode viver no PC ou na RAM do microcontrolador. O robô aqui usa a versão embarcada.

AÇÃO
Aponte para as três colunas do slide: simulador, ponte e robô.`,

  "15": `SLIDE 15 · POR QUE IMPORTA · VERSÃO ESTENDIDA (+0:40–1:10)

FALA
Por que isso importa? Porque é inteligência artificial rodando local, sem nuvem, com 24 números e um microcontrolador barato. É a ideia de edge AI: decidir perto de onde a ação acontece.
E é uma forma muito concreta de ensinar reforço: dá para ver a tabela mudando.

AÇÃO
Sem pressa. Deixe a frase “sem nuvem” cair.`,

  "16": `SLIDE 16 · LIMITES · VERSÃO ESTENDIDA (+1:10–1:40)

FALA
E o que ele ainda não sabe? Oito estados é pouco para curvas fechadas e cruzamentos. A linha ainda pode ser perdida. E o simulador não é o chão de verdade: atrito, ruído e bateria mudam o jogo.
Os próximos passos são mais sensores, câmera e estados contínuos. O próximo passo é sair do discreto — e continuar aprendendo.

AÇÃO
Aponte para o “8 → ∞” e depois para a lista de próximos passos.`,

  "17": `SLIDE 17 · FECHAMENTO · 6:35–7:00

FALA
Então, voltando à pergunta do começo: como um robô aprende? Ele não nasceu sabendo. Ele tentou, errou, recebeu notas e ajustou uma tabela de 24 números. Isso é aprendizado por reforço.
E o robô está aqui do lado: eu posso colocá-lo na pista agora. Enquanto ele anda, reparem nos sensores e nas rodas. E me perguntem: e se a linha acabar? Obrigado!

AÇÃO
Coloque o robô na pista e deixe-o rodar por 10–15 segundos antes de abrir para perguntas.`,

  "18": `APÊNDICE · Q-LEARNING

Se a banca pedir a conta:
Q[s,a] ← Q[s,a] + α · (r + γ · max Q[s′,a′] − Q[s,a])

α = 0,1 — taxa de aprendizado: quanto da novidade entra na nota.
γ = 0,9 — desconto do futuro: o quanto o amanhã importa.
ε = 1,0 → 0,13 — exploração: curiosidade que cai a cada episódio; mínimo 0,02.

Recompensa: centro +1,0 · lateral −0,5 · perdeu a linha −3,0.
O Q-update acontece antes da próxima escolha. A tabela é atualizada uma célula por passo.
Referência: Sutton & Barto, 2018, cap. 6.`,

  "19": `APÊNDICE · ANALOGIA

FALA
Se o robô fosse um bicho, ele seria um cachorro num parque com oito cheiros e três caminhos. Ele não nasce sabendo onde tem comida: ele cheira, escolhe, ganha um petisco ou um susto e ajusta o instinto.
A tabela é o instinto dele. Em vez de focinho, três sensores. Em vez de patas, dois motores. Em vez de uma tarde, um episódio. A curiosidade é o epsilon; a paciência com o futuro é o gamma.

AÇÃO
Aponte para a tabela “cachorro × robô” e depois para a equação traduzida. Se quiser, use esta analogia antes do slide 18.`,

  "20": `APÊNDICE · ARQUITETURAS

Quatro modos:
1 · if/else — robô físico, regras fixas, não aprende; é a linha de base.
2 · sim.py — ambiente e agente em Python, 100% simulado; treino rápido.
3 · onboard — agente embarcado no Arduino, sem PC e sem serial; robô autônomo.
4 · serial — ambiente no Python e agente no Arduino/ESP32; hardware-in-the-loop.

O modo 4 valida a Q-table no hardware antes de soltar o robô autônomo. O modo 3 é o que roda no robô da demo.`,

  "21": `APÊNDICE · NÚMEROS

Parâmetros: 200 episódios · até 1.000 passos por episódio · 8×3 = 24 notas · α=0,1 · γ=0,9 · ε 1,0→0,13.
Resultados: recompensa média −49 (primeiros 20) → +559 (últimos 20); melhor episódio +822; política aleatória 5 passos na linha × política aprendida 120 de 120.
Cuidado: são números do simulador. No robô real, atrito, ruído e bateria mudam o jogo.`,
};
